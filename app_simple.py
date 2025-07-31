# app.py - 간단한 테스트 앱
import streamlit as st
import time
from logging_config import logger, decorators, setup_logging

def main():
    st.title("🚀 로깅 시스템 테스트 앱")
    
    # 로깅 시스템 초기화
    setup_logging()
    
    st.write(f"현재 세션 ID: {st.session_state.get('session_id', '없음')}")
    st.write(f"사용자 ID: {st.session_state.get('user_id', '없음')}")
    
    # 테스트 버튼들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ 정상 작업"):
            test_normal_operation()
            st.success("정상 작업이 완료되었습니다!")
    
    with col2:
        if st.button("⚠️ 경고 생성"):
            test_warning()
            st.warning("경고가 생성되었습니다!")
    
    with col3:
        if st.button("❌ 에러 생성"):
            test_error()
            st.error("에러가 생성되었습니다!")
    
    # 성능 테스트
    st.subheader("성능 테스트")
    if st.button("🔄 무거운 작업 (3초)"):
        heavy_operation()
        st.success("무거운 작업이 완료되었습니다!")

@decorators.log_execution_time("normal_operation")
@decorators.log_user_action("test_normal")
def test_normal_operation():
    """정상 작업 테스트"""
    logger.info("정상 작업 시작")
    time.sleep(0.5)  # 시뮬레이션
    logger.info("정상 작업 완료", result="success")

def test_warning():
    """경고 테스트"""
    logger.warning("이것은 테스트 경고입니다", category="test")

def test_error():
    """에러 테스트"""
    try:
        # 의도적으로 에러 발생
        result = 1 / 0
    except Exception as e:
        logger.error("테스트 에러 발생", exception=e, test_type="division_by_zero")

@decorators.log_execution_time("heavy_task")
@decorators.log_user_action("heavy_operation")
def heavy_operation():
    """무거운 작업 시뮬레이션"""
    logger.info("무거운 작업 시작")
    time.sleep(3)  # 3초 대기
    logger.info("무거운 작업 완료", duration="3_seconds")

if __name__ == "__main__":
    main()
