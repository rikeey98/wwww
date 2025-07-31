# app.py - 수정된 버전
import streamlit as st
import pandas as pd
from datetime import datetime
import time

# logging_config에서 필요한 클래스들을 import
from logging_config import StreamlitLogger, LoggingDecorators, SystemMonitor

# 전역 로거 객체들 초기화
@st.cache_resource
def init_logging_system():
    """로깅 시스템 초기화 (한 번만 실행)"""
    logger = StreamlitLogger(log_dir="./logs")  # 로컬 테스트용 경로
    decorators = LoggingDecorators(logger)
    monitor = SystemMonitor(logger)
    return logger, decorators, monitor

# 전역 객체 생성
logger, decorators, monitor = init_logging_system()

def setup_logging():
    """세션별 로깅 초기화"""
    # 세션 ID 생성 (한 번만)
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # 사용자 ID 설정
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "anonymous"
    
    # 앱 시작 로그
    logger.access_log(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        action="app_start",
        page="main"
    )

def main():
    st.set_page_config(
        page_title="데이터 분석 대시보드",
        layout="wide"
    )
    
    # 로깅 시스템 초기화 (앱 시작시 한번만)
    setup_logging()
    
    st.title("🏢 기업 데이터 분석 시스템")
    
    # 사이드바 - 사용자 정보
    with st.sidebar:
        user_login()
    
    # 로그인 상태 확인
    if not st.session_state.get('logged_in', False):
        st.warning("로그인이 필요합니다.")
        return
    
    # 메인 콘텐츠 (로그인된 사용자만)
    tab1, tab2, tab3 = st.tabs(["📊 데이터 분석", "📈 리포트", "⚙️ 설정"])
    
    with tab1:
        data_analysis_page()
    
    with tab2:
        report_page()
    
    with tab3:
        settings_page()

def user_login():
    """사용자 로그인 처리"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.subheader("🔐 로그인")
        username = st.text_input("사용자 ID")
        password = st.text_input("비밀번호", type="password")
        
        if st.button("로그인"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user_id = username
                
                # 로그인 로깅
                logger.access_log(
                    user_id=username,
                    session_id=st.session_state.session_id,
                    action="login",
                    ip="localhost",
                    success=True
                )
                st.success("로그인 성공!")
                st.rerun()
            else:
                # 실패한 로그인 시도 로깅
                logger.access_log(
                    user_id=username,
                    session_id=st.session_state.session_id,
                    action="login_failed",
                    ip="localhost"
                )
                st.error("로그인 실패!")
        
        # 테스트용 계정 정보 표시
        st.info("테스트 계정: admin / password123 또는 user / user123")
        
    else:
        st.success(f"환영합니다, {st.session_state.user_id}님!")
        if st.button("로그아웃"):
            logout_user()

@decorators.log_user_action("authenticate")
@decorators.log_execution_time("user_authentication")
def authenticate_user(username, password):
    """사용자 인증 (예시)"""
    logger.debug("사용자 인증 시도", username=username)
    
    # 실제 인증 로직 (DB 조회 등)
    # 여기서는 간단한 예시
    valid_users = {"admin": "password123", "user": "user123"}
    
    is_valid = valid_users.get(username) == password
    
    if is_valid:
        logger.info("사용자 인증 성공", username=username)
    else:
        logger.warning("사용자 인증 실패", username=username)
    
    return is_valid

def logout_user():
    """사용자 로그아웃"""
    logger.access_log(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        action="logout"
    )
    
    st.session_state.logged_in = False
    st.session_state.user_id = "anonymous"
    st.rerun()

@decorators.log_execution_time("data_analysis")
@decorators.log_user_action("view_data_analysis")
def data_analysis_page():
    """데이터 분석 페이지"""
    st.header("📊 데이터 분석")
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "CSV 파일을 업로드하세요", 
        type=['csv'],
        key="data_upload"
    )
    
    if uploaded_file is not None:
        try:
            # 파일 로딩 로깅
            logger.info(
                "파일 업로드됨",
                filename=uploaded_file.name,
                size_bytes=uploaded_file.size,
                user_id=st.session_state.user_id
            )
            
            df = load_and_process_data(uploaded_file)
            
            if df is not None:
                display_data_analysis(df)
                
        except Exception as e:
            logger.error("파일 처리 중 오류", exception=e, filename=uploaded_file.name)
            st.error("파일 처리 중 오류가 발생했습니다.")
    else:
        st.info("CSV 파일을 업로드하면 데이터 분석을 시작할 수 있습니다.")
        
        # 샘플 데이터 생성 버튼
        if st.button("샘플 데이터로 테스트"):
            df = create_sample_data()
            st.session_state['sample_df'] = df
            display_data_analysis(df)

def create_sample_data():
    """샘플 데이터 생성"""
    import numpy as np
    
    logger.info("샘플 데이터 생성")
    
    # 샘플 데이터 생성
    data = {
        'date': pd.date_range('2024-01-01', periods=100),
        'sales': np.random.randint(1000, 5000, 100),
        'profit': np.random.randint(100, 1000, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    }
    
    return pd.DataFrame(data)

@decorators.log_execution_time("data_loading")
@decorators.log_errors()
def load_and_process_data(uploaded_file):
    """데이터 로딩 및 전처리"""
    logger.info("데이터 로딩 시작", filename=uploaded_file.name)
    
    try:
        # CSV 읽기
        df = pd.read_csv(uploaded_file)
        logger.info("데이터 로딩 완료", rows=len(df), columns=len(df.columns))
        
        # 기본 전처리
        original_rows = len(df)
        df = df.dropna()
        logger.info("데이터 전처리 완료", 
                   original_rows=original_rows, 
                   final_rows=len(df),
                   dropped_rows=original_rows-len(df))
        
        return df
        
    except Exception as e:
        logger.error("데이터 로딩 실패", exception=e, filename=uploaded_file.name)
        raise

def display_data_analysis(df):
    """데이터 분석 결과 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 데이터 요약")
        st.write(f"총 행 수: {len(df):,}")
        st.write(f"총 열 수: {len(df.columns)}")
        st.dataframe(df.head(), use_container_width=True)
    
    with col2:
        st.subheader("📈 통계 정보")
        st.write(df.describe())
    
    # 차트 생성
    if st.button("차트 생성"):
        generate_charts(df)

@decorators.log_execution_time("chart_generation")
@decorators.log_user_action("generate_charts")
def generate_charts(df):
    """차트 생성"""
    logger.info("차트 생성 시작", columns=list(df.columns))
    
    try:
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) > 0:
            st.subheader("📊 숫자형 데이터 차트")
            st.line_chart(df[numeric_columns])
            logger.info("차트 생성 완료", chart_type="line", columns=len(numeric_columns))
        else:
            st.warning("숫자형 컬럼이 없어 차트를 생성할 수 없습니다.")
            logger.warning("차트 생성 실패 - 숫자형 컬럼 없음")
            
    except Exception as e:
        logger.error("차트 생성 중 오류", exception=e)
        st.error("차트 생성 중 오류가 발생했습니다.")

def report_page():
    """리포트 페이지"""
    st.header("📈 시스템 리포트")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("시스템 상태 확인"):
            check_system_status()
    
    with col2:
        if st.button("로그 분석 보고서"):
            show_log_analysis()

@decorators.log_execution_time("system_status_check")
def check_system_status():
    """시스템 상태 확인"""
    logger.info("시스템 상태 확인 시작")
    
    try:
        # 시스템 모니터링
        monitor.log_system_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CPU 사용률", "45%", "2%")
        
        with col2:
            st.metric("메모리 사용률", "67%", "-3%")
        
        with col3:
            st.metric("디스크 사용률", "23%", "1%")
        
        st.success("시스템 상태가 정상입니다!")
        logger.info("시스템 상태 확인 완료")
    except Exception as e:
        logger.error("시스템 상태 확인 중 오류", exception=e)
        st.error("시스템 상태 확인 중 오류가 발생했습니다.")

def show_log_analysis():
    """로그 분석 결과 표시"""
    try:
        from log_analyzer import LogAnalyzer
        
        analyzer = LogAnalyzer(log_dir="./logs")  # 로컬 경로로 수정
        report = analyzer.generate_report(hours=24)
        
        st.subheader("🔍 최근 24시간 활동 분석")
        
        # 에러 분석
        error_data = report.get('errors', {})
        if error_data.get('total_errors', 0) > 0:
            st.error(f"⚠️ 총 {error_data['total_errors']}개의 에러가 발생했습니다.")
            
            if error_data.get('error_types'):
                st.write("**에러 유형별 분류:**")
                for error_type, count in error_data['error_types'].items():
                    st.write(f"- {error_type}: {count}회")
        else:
            st.success("✅ 에러가 발생하지 않았습니다.")
        
        # 사용자 활동 분석
        activity_data = report.get('user_activity', {})
        if activity_data:
            st.subheader("👥 사용자 활동")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 활동", activity_data.get('total_activities', 0))
            with col2:
                st.metric("고유 사용자", activity_data.get('unique_users', 0))
            with col3:
                st.metric("고유 세션", activity_data.get('unique_sessions', 0))
        
        logger.info("로그 분석 보고서 생성 완료")
        
    except ImportError:
        st.error("log_analyzer.py 파일이 없거나 import할 수 없습니다.")
        logger.error("LogAnalyzer import 실패")
    except Exception as e:
        logger.error("로그 분석 중 오류", exception=e)
        st.error("로그 분석 중 오류가 발생했습니다.")

def settings_page():
    """설정 페이지"""
    st.header("⚙️ 시스템 설정")
    
    st.subheader("로깅 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 현재 로그 파일 크기 표시
        if st.button("로그 파일 상태 확인"):
            try:
                from log_analyzer import LogManager
                manager = LogManager(log_dir="./logs")
                sizes = manager.get_log_sizes()
                
                st.write("**현재 로그 파일 크기:**")
                for filename, size_mb in sizes.items():
                    st.write(f"- {filename}: {size_mb} MB")
                
                logger.info("로그 파일 상태 확인", file_sizes=sizes)
            except Exception as e:
                logger.error("로그 파일 상태 확인 중 오류", exception=e)
                st.error("로그 파일 상태 확인 중 오류가 발생했습니다.")
    
    with col2:
        # 로그 정리
        if st.button("오래된 로그 정리"):
            try:
                from log_analyzer import LogManager
                manager = LogManager(log_dir="./logs")
                cleaned = manager.cleanup_old_logs(days=7)  # 테스트용으로 7일로 단축
                
                if cleaned:
                    st.success(f"{len(cleaned)}개의 오래된 로그 파일을 정리했습니다.")
                    logger.info("로그 파일 정리 완료", cleaned_count=len(cleaned))
                else:
                    st.info("정리할 오래된 로그 파일이 없습니다.")
            except Exception as e:
                logger.error("로그 정리 중 오류", exception=e)
                st.error("로그 정리 중 오류가 발생했습니다.")
    
    # 세션 정보 표시
    st.subheader("세션 정보")
    st.write(f"**세션 ID:** {st.session_state.get('session_id', 'None')}")
    st.write(f"**사용자 ID:** {st.session_state.get('user_id', 'None')}")
    st.write(f"**로그인 상태:** {st.session_state.get('logged_in', False)}")

if __name__ == "__main__":
    main()
