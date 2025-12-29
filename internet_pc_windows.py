# internet_pc_windows.py
import tiktoken
import os
from pathlib import Path

print("📥 tiktoken 캐시 다운로드 중...")
enc = tiktoken.get_encoding("cl100k_base")
print("✅ 완료!")

# Windows 캐시 위치
cache_dir = Path.home() / "AppData" / "Local" / "tiktoken_cache"
print(f"\n📂 캐시 위치: {cache_dir}")

# 파일 목록 출력
if cache_dir.exists():
    print("\n📄 캐시 파일 목록:")
    for file in cache_dir.iterdir():
        file_size = file.stat().st_size / 1024  # KB
        print(f"  - {file.name} ({file_size:.1f} KB)")
else:
    print("⚠️  캐시 디렉토리가 없습니다.")
    
    # 대체 경로 확인
    alt_cache_dir = Path.home() / ".cache" / "tiktoken"
    if alt_cache_dir.exists():
        print(f"\n📂 대체 경로 발견: {alt_cache_dir}")
        for file in alt_cache_dir.iterdir():
            file_size = file.stat().st_size / 1024
            print(f"  - {file.name} ({file_size:.1f} KB)")

print("\n✅ 위 디렉토리를 폐쇄망 PC로 복사하세요!")
