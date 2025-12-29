from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

def build_vectordb(docs_dir: str, output_dir: str):
    """MD 문서들로 Vector DB 생성"""
    
    # 1. 문서 로드
    print("📂 문서 로드 중...")
    md_files = list(Path(docs_dir).rglob("*.md"))
    
    documents = []
    for file_path in md_files:
        try:
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents.extend(loader.load())
            print(f"  ✓ {file_path.name}")
        except Exception as e:
            print(f"  ✗ {file_path.name}: {e}")
    
    print(f"\n✅ 총 {len(documents)}개 문서 로드 완료")
    
    # 2. 분할
    print("\n✂️  청크 분할 중...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ {len(chunks)}개 청크 생성 완료")
    
    # 3. Embedding 설정
    print("\n🔗 Embedding 모델 연결 중...")
    embeddings = OpenAIEmbeddings(
        model="qwen3-embedding:8b",
        openai_api_base="http://localhost:11434/v1",
        openai_api_key="ollama"
    )
    
    # 4. Vector DB 생성
    print("\n💾 Vector DB 생성 중...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # 5. 저장
    vectorstore.save_local(output_dir)
    print(f"✅ Vector DB 저장 완료: {output_dir}")
    
    return vectorstore

# 실행
if __name__ == "__main__":
    vectorstore = build_vectordb(
        docs_dir="docs",
        output_dir="faiss_index"
    )
