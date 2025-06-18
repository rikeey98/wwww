import pymongo
import time
from datetime import datetime

# MongoDB 연결 설정
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["your_database"]  # 데이터베이스 이름 변경
collection = db["your_collection"]  # 컬렉션 이름 변경

print("MongoDB 모니터링 시작...")
print(f"데이터베이스: {db.name}")
print(f"컬렉션: {collection.name}")
print("-" * 50)

while True:
    try:
        # checked 필드가 없는 (아직 확인하지 않은) 문서들 찾기
        unchecked_documents = collection.find({
            "checked": {"$exists": False}
        })
        
        new_count = 0
        for doc in unchecked_documents:
            print(f"새로운 데이터: {doc}")
            
            # 해당 문서를 checked로 표시
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"checked": True, "checkedAt": datetime.now()}}
            )
            new_count += 1
        
        if new_count > 0:
            print(f"총 {new_count}개의 새로운 문서를 처리했습니다.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 새로운 데이터 없음")
        
        # 30초 대기
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n모니터링을 중단합니다.")
        break
    except Exception as e:
        print(f"오류 발생: {e}")
        time.sleep(30)

# 연결 종료
client.close()
