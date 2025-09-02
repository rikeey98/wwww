#!/usr/bin/env python3
"""
MongoDB에서 프로젝트를 다운로드하고 압축 해제
사용법: 
  python download.py --name "프로젝트명" --output ./output
  python download.py --name "프로젝트명" --version "1.0" --output ./output --overwrite
"""

import os
import sys
import argparse
import zipfile
import tempfile
import shutil
from pymongo import MongoClient
import gridfs

# MongoDB 설정
MONGO_URL = "mongodb://localhost:27017"
DATABASE = "projects"

def list_versions(name):
    """프로젝트의 모든 버전 조회"""
    try:
        client = MongoClient(MONGO_URL)
        db = client[DATABASE]
        fs = gridfs.GridFS(db)
        
        files = fs.find({"metadata.name": name}).sort("metadata.upload_date", -1)
        versions = []
        
        for file in files:
            versions.append({
                "version": file.metadata["version"],
                "date": file.metadata["upload_date"],
                "size": file.metadata["size"]
            })
        
        return versions
    except:
        return []
    finally:
        client.close()

def download_project(name, version, output_path, overwrite):
    """MongoDB에서 프로젝트 다운로드"""
    
    try:
        # MongoDB 연결
        client = MongoClient(MONGO_URL)
        db = client[DATABASE]
        fs = gridfs.GridFS(db)
        
        # 파일 검색
        query = {"metadata.name": name}
        if version:
            query["metadata.version"] = version
        
        file = fs.find_one(query, sort=[("metadata.upload_date", -1)])
        
        if not file:
            print(f"❌ 프로젝트를 찾을 수 없습니다: {name}")
            if not version:
                versions = list_versions(name)
                if versions:
                    print("\n📋 사용 가능한 버전:")
                    for v in versions:
                        print(f"   - {v['version']} ({v['date'].strftime('%Y-%m-%d %H:%M')})")
            return False
        
        # 출력 경로 확인
        if os.path.exists(output_path) and not overwrite:
            response = input(f"⚠️  '{output_path}'가 이미 존재합니다. 덮어쓰시겠습니까? [y/N]: ")
            if response.lower() != 'y':
                print("❌ 다운로드 취소됨")
                return False
        
        # 기존 폴더 삭제 (덮어쓰기 시)
        if os.path.exists(output_path) and overwrite:
            shutil.rmtree(output_path)
        
        # 임시 파일에 다운로드
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "downloaded.zip")
            
            print("⬇️  다운로드 중...")
            with open(zip_path, 'wb') as f:
                f.write(file.read())
            
            print("📂 압축 해제 중...")
            os.makedirs(output_path, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(output_path)
        
        print(f"✅ 다운로드 완료!")
        print(f"   프로젝트: {name}")
        print(f"   버전: {file.metadata['version']}")
        print(f"   위치: {os.path.abspath(output_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return False
    finally:
        client.close()

def list_projects():
    """모든 프로젝트 목록 조회"""
    try:
        client = MongoClient(MONGO_URL)
        db = client[DATABASE]
        fs = gridfs.GridFS(db)
        
        pipeline = [
            {"$group": {
                "_id": "$metadata.name",
                "latest_version": {"$max": "$metadata.version"},
                "latest_date": {"$max": "$metadata.upload_date"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"latest_date": -1}}
        ]
        
        projects = list(db.fs.files.aggregate(pipeline))
        
        if not projects:
            print("📁 저장된 프로젝트가 없습니다.")
            return
        
        print("📋 저장된 프로젝트 목록:")
        print("-" * 60)
        for project in projects:
            name = project["_id"]
            latest = project["latest_version"]
            date = project["latest_date"].strftime("%Y-%m-%d %H:%M")
            count = project["count"]
            print(f"   {name} (최신: v{latest}, {count}개 버전, {date})")
        
    except Exception as e:
        print(f"❌ 목록 조회 실패: {e}")
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="MongoDB에서 프로젝트 다운로드")
    parser.add_argument("--name", help="프로젝트 이름")
    parser.add_argument("--version", help="특정 버전 (생략시 최신 버전)")
    parser.add_argument("--output", help="출력 폴더")
    parser.add_argument("--overwrite", action="store_true", help="기존 폴더 덮어쓰기")
    parser.add_argument("--list", action="store_true", help="프로젝트 목록 보기")
    
    args = parser.parse_args()
    
    if args.list:
        list_projects()
        return
    
    if not args.name or not args.output:
        print("❌ --name과 --output이 필요합니다. (또는 --list 사용)")
        parser.print_help()
        sys.exit(1)
    
    success = download_project(args.name, args.version, args.output, args.overwrite)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
