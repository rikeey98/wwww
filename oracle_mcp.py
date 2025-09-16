# multi_user_oracle_server.py
import os
import oracledb
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Dict, List

# 환경변수 로드
load_dotenv()

# Oracle 환경 설정
os.environ['ORACLE_HOME'] = os.getenv('ORACLE_HOME')
os.environ['TNS_ADMIN'] = os.getenv('TNS_ADMIN')
oracledb.defaults.config_dir = os.getenv('TNS_ADMIN')

# 무조건 Thick 모드
oracledb.init_oracle_client(lib_dir=os.getenv('ORACLE_HOME'))

mcp = FastMCP("Multi-User Oracle 🏢")

def get_user_config(username: str) -> Dict[str, str]:
    """사용자별 연결 정보 가져오기"""
    # 대문자로 변환
    username = username.upper()
    
    user = os.getenv(f'ORACLE_USER_{username}')
    password = os.getenv(f'ORACLE_PASSWORD_{username}')
    tns = os.getenv(f'ORACLE_TNS_{username}')
    
    if not all([user, password, tns]):
        raise Exception(f"사용자 '{username}' 설정이 없습니다")
    
    return {"user": user, "password": password, "tns": tns, "username": username}

def get_connection(username: str):
    """사용자별 DB 연결"""
    try:
        config = get_user_config(username)
        return oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["tns"]
        )
    except Exception as e:
        raise Exception(f"사용자 '{username}' 연결 실패: {str(e)}")

@mcp.tool
def test_connection(username: str) -> str:
    """특정 사용자로 DB 연결 테스트"""
    try:
        config = get_user_config(username)
        
        with get_connection(username) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SYSDATE, USER, SYS_CONTEXT('USERENV', 'DB_NAME') FROM DUAL")
            result = cursor.fetchone()
            
            return f"""✅ 사용자 '{username}' 연결 성공!
연결 정보: {config['user']}@{config['tns']}
현재 시간: {result[0]}
DB 사용자: {result[1]}
데이터베이스: {result[2]}"""
            
    except Exception as e:
        return f"❌ 사용자 '{username}' 연결 실패: {str(e)}"

@mcp.tool
def get_available_users() -> List[str]:
    """사용 가능한 사용자 목록"""
    users = []
    
    # 환경변수에서 ORACLE_USER_로 시작하는 것들 찾기
    for key, value in os.environ.items():
        if key.startswith('ORACLE_USER_'):
            username = key.replace('ORACLE_USER_', '')
            tns = os.getenv(f'ORACLE_TNS_{username}')
            users.append(f"{username.lower()}: {value}@{tns}")
    
    return users if users else ["설정된 사용자가 없습니다"]

@mcp.tool
def get_tables(username: str) -> List[str]:
    """특정 사용자의 테이블 목록"""
    try:
        with get_connection(username) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM USER_TABLES ORDER BY TABLE_NAME")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                return [f"사용자 '{username}'에게 테이블이 없습니다"]
            
            return tables
            
    except Exception as e:
        return [f"오류: {str(e)}"]

@mcp.tool
def describe_table(username: str, table_name: str) -> List[Dict[str, str]]:
    """특정 사용자의 테이블 구조"""
    try:
        with get_connection(username) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, NULLABLE 
                   FROM USER_TAB_COLUMNS 
                   WHERE TABLE_NAME = UPPER(:1) 
                   ORDER BY COLUMN_ID""",
                (table_name,)
            )
            
            columns = cursor.fetchall()
            if not columns:
                return [{"error": f"테이블 '{table_name}' 찾을 수 없음"}]
            
            result = []
            for col in columns:
                result.append({
                    "column": col[0],
                    "type": col[1],
                    "length": str(col[2]) if col[2] else "",
                    "nullable": col[3]
                })
            
            return result
            
    except Exception as e:
        return [{"error": f"오류: {str(e)}"}]

@mcp.tool
def execute_query(username: str, sql: str, limit: int = 100) -> Dict:
    """특정 사용자로 쿼리 실행"""
    try:
        if not sql.strip().upper().startswith('SELECT'):
            return {"error": "SELECT 쿼리만 허용됩니다"}
        
        # 간단한 LIMIT 처리
        if 'ROWNUM' not in sql.upper() and limit > 0:
            sql = f"SELECT * FROM ({sql}) WHERE ROWNUM <= {limit}"
        
        with get_connection(username) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # 컬럼 정보
            columns = [desc[0] for desc in cursor.description]
            
            # 데이터 변환
            rows = []
            for row in cursor.fetchall():
                row_data = {}
                for i, value in enumerate(row):
                    if value is None:
                        row_data[columns[i]] = None
                    elif hasattr(value, 'strftime'):
                        row_data[columns[i]] = value.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        row_data[columns[i]] = str(value)
                rows.append(row_data)
            
            return {
                "username": username.lower(),
                "columns": columns,
                "row_count": len(rows),
                "data": rows
            }
            
    except Exception as e:
        return {"error": f"쿼리 실행 오류: {str(e)}"}

@mcp.tool
def test_all_connections() -> List[str]:
    """모든 설정된 사용자 연결 테스트"""
    results = []
    
    # 환경변수에서 모든 사용자 찾기
    for key, value in os.environ.items():
        if key.startswith('ORACLE_USER_'):
            username = key.replace('ORACLE_USER_', '')
            
            try:
                config = get_user_config(username)
                with get_connection(username) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT USER FROM DUAL")
                    db_user = cursor.fetchone()[0]
                    results.append(f"✅ {username.lower()}: {config['user']}@{config['tns']} - DB사용자: {db_user}")
            except Exception as e:
                results.append(f"❌ {username.lower()}: 연결실패 - {str(e)}")
    
    return results if results else ["설정된 사용자가 없습니다"]

@mcp.tool
def get_user_info(username: str) -> str:
    """특정 사용자의 설정 정보"""
    try:
        config = get_user_config(username)
        return f"""사용자 '{username.lower()}' 정보:
- DB 사용자: {config['user']}
- TNS: {config['tns']}
- 설정 이름: {config['username']}"""
    except Exception as e:
        return f"사용자 '{username}' 정보를 찾을 수 없습니다: {str(e)}"

if __name__ == "__main__":
    print("Multi-User Oracle MCP Server 시작")
    mcp.run()
