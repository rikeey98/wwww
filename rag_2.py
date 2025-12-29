# soc_automation/rag/build_vectordb.py

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.vectorstores import FAISS

# 1. Ollama Embedding
embeddings = OpenAIEmbeddings(
    model="qwen3-embedding:8b",
    openai_api_base="http://localhost:11434/v1",
    openai_api_key="ollama"
)

# 2. MD 파일 로드
loader = DirectoryLoader(
    "config/prompts/error_analyzer/sub_agents/",
    glob="**/*.md",
    loader_cls=lambda path: MarkdownTextSplitter().create_documents([open(path).read()])
)
documents = loader.load()

# 3. Vector DB 생성
vectorstore = FAISS.from_documents(documents, embeddings)

# 4. 저장
vectorstore.save_local("rag/faiss_index")

print(f"✅ {len(documents)}개 문서 → Vector DB 생성 완료")
