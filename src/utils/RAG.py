import os

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma, FAISS

def load_document(file):
    """
    加载PDF、DOC、TXT文档
    :param file:
    :return:
    """
    name, extension = os.path.splitext(file)

    if extension == '.pdf':
        print(f'Loading {file}')
        loader = PyPDFLoader(file)
    elif extension == '.docx':
        print(f'Loading {file}')
        loader = Docx2txtLoader(file)
    elif extension == '.txt':
        loader = UnstructuredFileLoader(file)
    else:
        print('Document format is not supported!')
        return None
    data = loader.load()
    return data


def chunk_data(data, chunk_size=256, chunk_overlap=150):
    """
    将数据分割成块
    :param data:
    :param chunk_size: chunk块大小
    :param chunk_overlap: 重叠部分大小
    :return:
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(data)
    return chunks


def get_embedding(embedding_name):
    """
    根据embedding名称去加载embedding模型
    :param embedding_name: 路径或者名称
    :return:
    """
    if embedding_name == "bge":
        model_name = "BAAI/bge-small-en"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}
        hf = HuggingFaceBgeEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )
        return hf
    if embedding_name == "bce":
        return None


# create embeddings using OpenAIEmbeddings() and save them in a Chroma vector store
def create_embeddings_chroma(chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(chunks, embeddings)

    # if you want to use a specific directory for chromadb
    # vector_store = Chroma.from_documents(chunks, embeddings, persist_directory='./mychroma_db')
    return vector_store


def create_embeddings_faiss(vector_db_path, embedding_name, chunks):
    """
    使用FAISS向量数据库，并保存
    :param vector_db_path: 向量
    :param embedding_name:
    :param chunks:
    :return:
    """
    embeddings = get_embedding(embedding_name)
    db = FAISS.from_documents(chunks, embeddings)

    if not os.path.isdir(vector_db_path):
        os.mkdir(vector_db_path)

    db.save_local(folder_path=vector_db_path)
    return db


def load_embeddings_faiss(vector_db_path, embedding_name):
    """
    加载向量库
    :param vector_db_path:
    :param embedding_name:
    :return:
    """
    embeddings = get_embedding(embedding_name)
    db = FAISS.load_local(vector_db_path, embeddings, allow_dangerous_deserialization=True)
    return db


if __name__ == "__main__":
    file_path = "test.txt"  # 可替换为 test.pdf / test.docx
    docs = load_document(file_path)
    chunks = chunk_data(docs)
    # 构建并保存向量库
    vector_db_path = "my_faiss_db"
    db = create_embeddings_faiss(vector_db_path, "bge", chunks)
    print(f"向量库已保存到 {vector_db_path}")

    # 加载向量库并检索
    db = load_embeddings_faiss(vector_db_path, "bge")
    query = "杭州有什么景点？"
    results = db.similarity_search(query, k=2)

    print("\n🔍 检索结果：")
    for i, doc in enumerate(results):
        print(f"\n--- 相似段落 {i + 1} ---\n{doc.page_content}")