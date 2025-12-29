from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# =============================================
# 1. Embedding 모델 설정 (로컬 Ollama)
# =============================================
embeddings = OpenAIEmbeddings(
    model="qwen3-embedding:8b",
    openai_api_base="http://localhost:11434/v1",
    openai_api_key="ollama"  # 더미값
)

# =============================================
# 2. 문서 로드
# =============================================
loader = DirectoryLoader(
    "docs/",
    glob="**/*.md"
)
documents = loader.load()

# =============================================
# 3. 문서 분할 (청크 단위)
# =============================================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

print(f"문서 {len(documents)}개 → 청크 {len(chunks)}개로 분할")

# =============================================
# 4. Vector DB 생성 (문서를 벡터로 변환하여 저장)
# =============================================
vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)

# 디스크에 저장 (재사용 가능)
vectorstore.save_local("faiss_index")

print("✅ Vector DB 생성 완료!")

# =============================================
# 5. LLM 설정 (답변 생성용)
# =============================================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key="sk-xxx"
)

# =============================================
# 6. RAG 체인 구성
# =============================================
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 3}  # 상위 3개 문서 검색
    )
)

# =============================================
# 7. 질문하기
# =============================================
question = "MEM-001 패턴이 뭐야?"

result = qa_chain.invoke({"query": question})

print(result["result"])
