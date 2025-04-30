from fastapi import APIRouter, HTTPException
from src.utils.RAG import *

RAG = APIRouter()

@RAG.get('/', description="获得所有餐厅")
async def test():
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