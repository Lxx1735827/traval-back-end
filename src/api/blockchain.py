from fastapi import APIRouter, HTTPException, Request
import sys
import json
import time
import os
import signal
import atexit
import requests
from src.utils.blockchain_utils import *
from src.schema import *

bc_url = "http://localhost:8000/bc"
bc = APIRouter()

# the node's copy of blockchain
blockchain = None

# the address to other participating members of the network
peers = set()

# 向指定节点发送请求以加入peers
def register(peer_address, peer_port):
    try:
        # 需要请求的Peer数据
        peer_data = PeerSchema(node_address=peer_address, node_port=peer_port)

        # 假设`register_with_existing_node`已经定义用于处理这种注册的路由
        response = requests.post(f"http://{peer_address}:{peer_port}/register_node", json=peer_data.dict())

        if response.status_code == 200:
            print(f"Successfully registered with peer {peer_address}:{peer_port}")
        else:
            print(f"Failed to register with peer {peer_address}:{peer_port}. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error while trying to register with {peer_address}:{peer_port}: {e}")

# register("", "")

@bc.post("/new_transaction", description="提交新的transaction到该node的blockchain里")
def new_transaction(transaction: TransactionSchema):
    tx_data = transaction.dict()
    required_fields = ["content", "timestamp"]

    for field in required_fields:
        if not tx_data.get(field):
            return HTTPException(status_code=404, detail="Invalid transaction data")

    # tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    try:
        response = requests.post(f"{bc_url}/mine")  # 挖矿 API
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to mine block.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error triggering mining process")

    return {"data": "Transaction added and mining started."}

# 从多个block的list创建blockchain
def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        generated_blockchain.add_block(block, proof)
    return generated_blockchain

@bc.get("/chain", description="获取该node的blockchain的信息")
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# 服务器中存储的区块链文件
chain_file_name = os.environ.get('BLOCKCHAIN_DATA_FILE')

# 将最新的区块链信息存储当本地文件中
def save_chain():
    if chain_file_name is not None:
        # 获取区块链的最新状态
        chain_data = get_chain()
        # 保证写入时将其转换为正确的格式
        with open(chain_file_name, 'w') as chain_file:
            chain_file.write(chain_data)


def exit_from_signal(signum, stack_frame):
    sys.exit(0)


atexit.register(save_chain)
signal.signal(signal.SIGTERM, exit_from_signal)
signal.signal(signal.SIGINT, exit_from_signal)

if chain_file_name is None:
    data = None

else:
    # 读取区块链文件
    if os.path.exists(chain_file_name):
        with open(chain_file_name, 'r') as chain_file:
            raw_data = chain_file.read()
            if raw_data:
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    data = None
            else:
                data = None
    else:
        data = None

if data is None:
    # the node's copy of blockchain
    blockchain = Blockchain()
else:
    blockchain = create_chain_from_dump(data['chain'])
    peers.update(data['peers'])

@bc.get("/mine", description="mine未经确认的transaction")
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return {"data": "No transactions to mine"}
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
            print(f"Block #{blockchain.last_block.index} is mined.")
            return {"data": f"Block {blockchain.last_block.index} is mined"}

@bc.post("/register_node", description="将新的node加入到该node的peers")
def register_new_peers(peer: PeerSchema):
    node_address = peer.node_address
    node_port = peer.node_port
    if not node_address or not node_port:
        raise HTTPException(status_code=400, detail="Invalid data")

    peers.add(peer)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@bc.post("/register_with", description="将新的node加入到该node和其他node的peers中")
def register_with_existing_node(peer: PeerSchema, request: Request):
    # 请求加入的已存在node
    node_address = peer.node_address
    node_port = peer.node_port
    if not node_address or not node_port:
        return HTTPException(status_code=400, detail="Invalid data")

    # new node
    data = {"node_address": request.client.host,
            "node_port": request.client.port}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    remote_url = f"http://{node_address}:{node_port}/register_node"
    response = requests.post(remote_url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()["chain"]
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()["peers"])
        return {"data": "Successfully register"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.content)


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@bc.post("/add_block", description="")
def verify_and_add_block(block_data: BlockSchema):

    block = Block(block_data.index,
                  block_data.transactions,
                  block_data.timestamp,
                  block_data.previous_hash,
                  block_data.nonce)

    proof = block_data.hash
    try:
        blockchain.add_block(block, proof)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="The block was discarded by the node: " + e.str())

    return {"data": "Block added to the chain"}


@bc.get("pending_tx", description="获取未被确认的transactions")
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# 校正该node的blockchain，以最长的为准
def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        try:
            remote_url = f"http://{node.node_address}:{node.node_port}/chain"
            response = requests.get(remote_url)
            length = response.json()['length']
            chain = response.json()['chain']
            if length > current_len and blockchain.check_chain_validity(chain):
                current_len = length
                longest_chain = chain
        except:
            raise HTTPException(status_code=400, detail="Failed to get peer's info of chain")

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

# announce to the network(all peers) once a block has been mined
def announce_new_block(block):
    for peer in peers:
        remote_url = f"http://{peer.node_address}:{peer.node_port}/add_block"
        headers = {'Content-Type': "application/json"}
        requests.post(remote_url,
                  data=json.dumps(block.__dict__, sort_keys=True),
                  headers=headers)
