#!/usr/bin/env python3
"""
프로젝트를 압축해서 MongoDB에 업로드
사용법: python upload.py --project ./my-project --name "프로젝트명" --version "1.0"
"""

import os
import sys
import argparse
import zipfile
import tempfile
from datetime import datetime
from pymongo import MongoClient
import gridfs

# MongoDB 설정
MONGO_URL = "mongodb://localhost:27017"
DATABASE = "projects"

def create_zip(project_path, temp_dir):
    """프로젝트 폴더를 ZIP으로 압축"""
    zip_path = os.path.join(temp_dir, "project.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            # .git, __pycache__ 등 제외
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if not file.startswith('.') and not file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arc_path)
    
    return zip_path

def upload_project(project_path, name, version):
    """프로젝트를 MongoDB에 업로드"""
    if not os.path.exists(project_path):
        print(f"❌ 프로젝트 경로가 존재하지 않습니다: {project_path}")
        return False
    
    try:
        # MongoDB 연결
        client = MongoClient(MONGO_URL)
        db = client[DATABASE]
        fs = gridfs.GridFS(db)
        
        # 임시 디렉토리에서 압축
        with tempfile.TemporaryDirectory() as temp_dir:
            print("📦 프로젝트 압축 중...")
            zip_path = create_zip(project_path, temp_dir)
            zip_size = os.path.getsize(zip_path)
            
            # GridFS에 업로드
            print("⬆️  MongoDB에 업로드 중...")
            with open(zip_path, 'rb') as f:
                file_id = fs.put(
                    f,
                    filename=f"{name}_v{version}.zip",
                    metadata={
                        "name": name,
                        "version": version,
                        "upload_date": datetime.now(),
                        "size": zip_size,
                        "original_path": os.path.abspath(project_path)
                    }
                )
        
        print(f"✅ 업로드 완료!")
        print(f"   프로젝트: {name}")
        print(f"   버전: {version}")
        print(f"   크기: {zip_size:,} bytes")
        print(f"   ID: {file_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 업로드 실패: {e}")
        return False
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="프로젝트를 MongoDB에 업로드")
    parser.add_argument("--project", required=True, help="프로젝트 폴더 경로")
    parser.add_argument("--name", required=True, help="프로젝트 이름")
    parser.add_argument("--version", required=True, help="버전")
    
    args = parser.parse_args()
    
    success = upload_project(args.project, args.name, args.version)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
