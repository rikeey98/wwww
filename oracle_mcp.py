import os
import oracledb
from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List, Dict, Any

# 환경변수 로드
load_dotenv()

mcp = FastMCP("Oracle DB Helper (TNS) 🗄️")

def get_db_connection():
    """Oracle DB TNS 연결 생성"""
    try:
        # TNS_ADMIN 경로 설정 (선택사항)
        tns_admin = os.getenv('TNS_ADMIN')
        if tns_admin:
            oracledb.defaults.config_dir = tns_admin
        
        user = os.getenv('ORACLE_USER')
        password = os.getenv('ORACLE_PASSWORD')
        
        # 연결 방법 선택
        tns_name = os.getenv('ORACLE_TNS_NAME')
        connection_string = os.getenv('ORACLE_CONNECTION_STRING')
        tns_string = os.getenv('ORACLE_TNS_STRING')
        
        if tns_name:
            # 방법 1: TNS 이름 사용 (tnsnames.ora에 정의된 이름)
            dsn = tns_name
            print(f"TNS 이름으로 연결: {tns_name}")
            
        elif connection_string:
            # 방법 2: Easy Connect 문자열 사용
            dsn = connection_string
            print(f"Easy Connect로 연결: {connection_string}")
            
        elif tns_string:
            # 방법 3: 전체 TNS 문자열 사용
            dsn = tns_string
            print("TNS 문자열로 연결")
            
        else:
            raise Exception("TNS 연결 정보가 설정되지 않았습니다")
        
        connection = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        
        return connection
        
    except Exception as e:
        raise Exception(f"DB 연결 실패: {str(e)}")

@mcp.tool
def get_connection_info() -> Dict[str, Any]:
    """현재 DB 연결 정보를 반환합니다"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 연결 정보 쿼리들
            queries = {
                "instance": "SELECT INSTANCE_NAME FROM V$INSTANCE",
                "database": "SELECT NAME FROM V$DATABASE", 
                "version": "SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1",
                "current_schema": "SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL",
                "session_user": "SELECT USER FROM DUAL",
                "server_host": "SELECT SYS_CONTEXT('USERENV', 'SERVER_HOST') FROM DUAL"
            }
            
            info = {}
            for key, query in queries.items():
                try:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    info[key] = result[0] if result else "N/A"
                except Exception as e:
                    info[key] = f"조회 실패: {str(e)}"
            
            return info
            
    except Exception as e:
        return {"error": f"연결 정보 조회 실패: {str(e)}"}

@mcp.tool
def get_table_structure(table_name: str) -> Dict[str, Any]:
    """테이블 구조 정보를 반환합니다"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 테이블 컬럼 정보 조회
            query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                DATA_LENGTH,
                DATA_PRECISION,
                DATA_SCALE,
                NULLABLE,
                DATA_DEFAULT,
                COLUMN_ID
            FROM ALL_TAB_COLUMNS 
            WHERE TABLE_NAME = UPPER(:table_name)
            AND OWNER = USER
            ORDER BY COLUMN_ID
            """
            
            cursor.execute(query, {"table_name": table_name})
            columns = cursor.fetchall()
            
            if not columns:
                return {"error": f"테이블 '{table_name}'을 찾을 수 없습니다"}
            
            structure = {
                "table_name": table_name.upper(),
                "columns": []
            }
            
            for col in columns:
                col_info = {
                    "name": col[0],
                    "type": col[1],
                    "length": col[2],
                    "precision": col[3],
                    "scale": col[4],
                    "nullable": col[5],
                    "default": col[6],
                    "position": col[7]
                }
                structure["columns"].append(col_info)
            
            return structure
            
    except Exception as e:
        return {"error": f"오류 발생: {str(e)}"}

@mcp.tool
def execute_select_query(query: str, limit: int = 100) -> Dict[str, Any]:
    """SELECT 쿼리를 실행하고 결과를 반환합니다"""
    try:
        if not query.strip().upper().startswith('SELECT'):
            return {"error": "SELECT 쿼리만 허용됩니다"}
        
        if 'ROWNUM' not in query.upper() and limit > 0:
            query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
            # 간단한 컬럼 정보 (이름만)
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # 데이터 가져오기
            rows = cursor.fetchall()
            
            result = {
                "columns": column_names,
                "row_count": len(rows),
                "data": []
            }
            
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    col_name = column_names[i]
                    
                    # 간단한 값 변환
                    if hasattr(value, 'strftime'):  # 날짜
                        row_dict[col_name] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif value is None:
                        row_dict[col_name] = None
                    else:
                        row_dict[col_name] = str(value)
                        
                result["data"].append(row_dict)
            
            return result
            
    except Exception as e:
        return {"error": f"쿼리 실행 오류: {str(e)}"}

@mcp.tool
def get_table_list(schema: str = None) -> List[Dict[str, str]]:
    """테이블 목록을 반환합니다"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if schema:
                query = """
                SELECT TABLE_NAME, OWNER, NUM_ROWS 
                FROM ALL_TABLES 
                WHERE OWNER = UPPER(:schema)
                ORDER BY TABLE_NAME
                """
                cursor.execute(query, {"schema": schema})
            else:
                query = """
                SELECT TABLE_NAME, OWNER, NUM_ROWS 
                FROM USER_TABLES 
                ORDER BY TABLE_NAME
                """
                cursor.execute(query)
            
            tables = []
            for row in cursor.fetchall():
                tables.append({
                    "table_name": row[0],
                    "owner": row[1],
                    "num_rows": str(row[2]) if row[2] else "Unknown"
                })
            
            return tables
            
    except Exception as e:
        return [{"error": f"테이블 목록 조회 실패: {str(e)}"}]

@mcp.tool
def test_connection() -> str:
    """TNS DB 연결 테스트"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SYSDATE, USER, SYS_CONTEXT('USERENV', 'DB_NAME') FROM DUAL")
            result = cursor.fetchone()
            return f"TNS 연결 성공!\n현재 시간: {result[0]}\n사용자: {result[1]}\n데이터베이스: {result[2]}"
    except Exception as e:
        return f"TNS 연결 실패: {str(e)}"

@mcp.resource("config://oracle-tns")
def get_oracle_tns_config() -> Dict[str, str]:
    """Oracle TNS 연결 설정 정보"""
    config = {
        "user": os.getenv('ORACLE_USER', ''),
        "tns_name": os.getenv('ORACLE_TNS_NAME', ''),
        "connection_string": os.getenv('ORACLE_CONNECTION_STRING', ''),
        "tns_admin": os.getenv('TNS_ADMIN', ''),
        "connection_type": ""
    }
    
    if config["tns_name"]:
        config["connection_type"] = "TNS Name"
    elif config["connection_string"]:
        config["connection_type"] = "Easy Connect"
    elif os.getenv('ORACLE_TNS_STRING'):
        config["connection_type"] = "TNS String"
    else:
        config["connection_type"] = "Not Configured"
    
    return config

if __name__ == "__main__":
    mcp.run()
