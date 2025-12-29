# download_tiktoken_cache.py
import requests
from pathlib import Path
import hashlib

# SSL 검증 비활성화
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_tiktoken_cache():
    """tiktoken 캐시 파일 직접 다운로드"""
    
    # cl100k_base 인코딩 파일 URL
    url = "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
    
    # Windows 캐시 경로
    cache_dir = Path.home() / "AppData" / "Local" / "tiktoken_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 다운로드 중: {url}")
    print(f"📂 저장 위치: {cache_dir}")
    
    try:
        # verify=False로 다운로드
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
        
        # 파일 내용
        content = response.content
        
        # 파일명은 내용의 SHA256 해시
        file_hash = hashlib.sha256(content).hexdigest()
        
        # 저장
        cache_file = cache_dir / file_hash
        cache_file.write_bytes(content)
        
        print(f"✅ 다운로드 완료!")
        print(f"📄 파일명: {file_hash}")
        print(f"📏 크기: {len(content) / 1024:.1f} KB")
        
        return cache_file
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return None

if __name__ == "__main__":
    cache_file = download_tiktoken_cache()
    
    if cache_file:
        print("\n✅ 성공! 이제 tiktoken을 사용할 수 있습니다.")
        
        # 테스트
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        print("✅ tiktoken 로드 성공!")
