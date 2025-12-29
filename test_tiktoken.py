# test_tiktoken.py
import tiktoken
import os

# 캐시 위치 확인
cache_dir = os.path.expanduser("~/.cache/tiktoken")
print(f"📂 캐시 디렉토리: {cache_dir}")
print(f"📁 존재 여부: {os.path.exists(cache_dir)}")

if os.path.exists(cache_dir):
    print("\n📄 캐시 파일:")
    for file in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, file)
        file_size = os.path.getsize(file_path) / 1024
        print(f"  - {file} ({file_size:.1f} KB)")

# tiktoken 로드 테스트
try:
    print("\n🔄 tiktoken 로드 중...")
    enc = tiktoken.get_encoding("cl100k_base")
    print("✅ 성공! (오프라인 작동)")
    
    # 인코딩 테스트
    text = "Hello, world!"
    tokens = enc.encode(text)
    print(f"✅ 인코딩 테스트: '{text}' → {tokens}")
    
except Exception as e:
    print(f"❌ 실패: {e}")
    print("\n💡 문제 해결:")
    print("1. 파일명이 올바른지 확인")
    print("2. 파일 권한 확인: chmod 644 ~/.cache/tiktoken/*")
    print("3. 환경변수 설정: export TIKTOKEN_CACHE_DIR=~/.cache/tiktoken")
