# 맞습니다! 정확히 이해하셨어요

---

## 1. Ollama로 로컬 설치 → URL 생성

```bash
# 1. Ollama 설치 (이미 했으면 스킵)
# Windows: https://ollama.com/download

# 2. qwen3-embedding 모델 다운로드
ollama pull qwen3-embedding:8b

# 3. 자동으로 서버 실행됨
# URL: http://localhost:11434/v1
```

**이제 이 URL을 OpenAI API처럼 사용 가능!**

---

## 2. LangChain에서 RAG 구축

### RAG란?
**문서 → Vector DB 변환 → 유사도 검색 → LLM 답변**

```
┌─────────────────────────────────────┐
│        RAG 전체 흐름                │
├─────────────────────────────────────┤
│                                      │
│  [1] 문서 준비                      │
│      ├─ MD 파일들                   │
│      └─ PDF, TXT 등                 │
│           ↓                          │
│  [2] Embedding 모델 (qwen3)         │
│      ├─ 문서를 벡터로 변환          │
│      └─ http://localhost:11434/v1   │
│           ↓                          │
│  [3] Vector DB 저장                 │
│      ├─ FAISS (로컬 파일)           │
│      ├─ Chroma (SQLite)             │
│      └─ Qdrant (Docker)             │
│           ↓                          │
│  [4] 질문 시 검색                   │
│      ├─ 질문을 벡터로 변환          │
│      ├─ 유사한 문서 찾기            │
│      └─ 상위 K개 문서 반환          │
│           ↓                          │
│  [5] LLM 답변 생성                  │
│      └─ 찾은 문서 + 질문 → 답변    │
└─────────────────────────────────────┘
```

---

## 3. 전체 코드 예시

```python
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
```

---

## 4. 실행 흐름 상세

### ① 문서 로드 & 분할
```python
# 100개 MD 파일 → 500개 청크
documents = loader.load()  # [Doc1, Doc2, ...]
chunks = text_splitter.split_documents(documents)  # [Chunk1, Chunk2, ...]
```

### ② Vector DB 생성 (핵심!)
```python
# 내부 동작:
for chunk in chunks:
    # Ollama API 호출
    response = requests.post(
        "http://localhost:11434/v1/embeddings",
        json={"input": chunk.page_content, "model": "qwen3-embedding:8b"}
    )
    vector = response.json()["data"][0]["embedding"]
    # [0.123, -0.456, ..., 0.789]
    
    # FAISS에 저장
    vectorstore.add(vector, metadata=chunk.metadata)
```

**결과:** `faiss_index/` 폴더에 저장됨

### ③ 질문 시 검색
```python
# 1. 질문을 벡터로 변환
question_vector = embeddings.embed_query("MEM-001이 뭐야?")

# 2. 유사도 계산 (코사인 유사도)
similar_docs = vectorstore.similarity_search(
    "MEM-001이 뭐야?",
    k=3
)

# 3. 결과
# [
#   Document(page_content="MEM-001: Cache coherency violation...", metadata={"source": "patterns.md"}),
#   Document(page_content="MEM-001 심각도는 9입니다...", metadata={"source": "severity.md"}),
#   ...
# ]
```

### ④ LLM 답변 생성
```python
# 찾은 문서 + 질문을 프롬프트로 조합
prompt = f"""
다음 문서를 참고해서 질문에 답하세요:

문서1: {similar_docs[0].page_content}
문서2: {similar_docs[1].page_content}
문서3: {similar_docs[2].page_content}

질문: MEM-001이 뭐야?
"""

# LLM 호출
answer = llm.invoke(prompt)
```

---

## 5. Vector DB 재사용

```python
# 한 번 생성한 Vector DB는 재사용 가능
from langchain_community.vectorstores import FAISS

# 로드만 하면 됨 (다시 임베딩 안해도 됨!)
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)

# 바로 검색 가능
results = vectorstore.similarity_search("MEM-001", k=3)
```

---

## 6. 당신 프로젝트 적용

### 폴더 구조
```
soc_automation/
├── config/
│   └── prompts/
│       └── error_analyzer/
│           └── sub_agents/
│               ├── pattern_matcher.md       # 100+ 패턴
│               ├── severity_assessor.md
│               └── root_cause_analyzer.md
└── rag/
    ├── build_vectordb.py     # Vector DB 생성 스크립트
    ├── faiss_index/          # 저장된 Vector DB
    └── search.py             # 검색 함수
```

### Vector DB 생성 스크립트
```python
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
```

### 검색 함수
```python
# soc_automation/rag/search.py

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def search_patterns(error_message: str, k: int = 5) -> list:
    """에러 메시지로 유사한 패턴 검색"""
    
    # Embedding 설정
    embeddings = OpenAIEmbeddings(
        model="qwen3-embedding:8b",
        openai_api_base="http://localhost:11434/v1",
        openai_api_key="ollama"
    )
    
    # Vector DB 로드
    vectorstore = FAISS.load_local(
        "rag/faiss_index",
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
    
    # 검색
    results = vectorstore.similarity_search(
        error_message,
        k=k
    )
    
    return results

# 사용 예시
if __name__ == "__main__":
    results = search_patterns("Cache coherency violation detected")
    
    for doc in results:
        print(doc.page_content[:200])
        print(doc.metadata)
        print("---")
```

### Agent에서 사용
```python
# soc_automation/agents/error_analyzer/sub_agents/pattern_matcher.py

from soc_automation.rag.search import search_patterns

async def pattern_matcher_node(state):
    error_message = state['error_message']
    
    # RAG로 유사 패턴 검색
    similar_patterns = search_patterns(error_message, k=5)
    
    # LLM에게 검색 결과와 함께 전달
    prompt = f"""
    에러 메시지: {error_message}
    
    유사한 패턴들:
    {chr(10).join([doc.page_content for doc in similar_patterns])}
    
    위 패턴 중 가장 일치하는 것을 선택하세요.
    """
    
    # LLM 호출...
```

---

## 7. 정리

| 단계 | 설명 | 한 번만? |
|------|------|----------|
| **Ollama 설치** | `ollama pull qwen3-embedding:8b` | ✅ 한 번만 |
| **Vector DB 생성** | 문서 → 벡터 변환 → 저장 | ✅ 한 번만 |
| **검색** | 질문 → 벡터 변환 → 유사도 검색 | 매번 |
| **LLM 답변** | 검색 결과 + 질문 → 답변 | 매번 |

**RAG = Vector DB 만들기 + 유사도 검색 + LLM 답변**

당신이 이해한 것이 100% 맞습니다! 🎯
