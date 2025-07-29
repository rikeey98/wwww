import streamlit as st
from datetime import datetime

def generate_log_filename(input_date):
    """
    input_date를 기반으로 로그 파일명을 생성
    
    Args:
        input_date: datetime 객체 또는 'YYYY-MM-DD' 형식의 문자열
    
    Returns:
        str: 생성된 로그 파일명
    """
    # 오늘 날짜
    today = datetime.now().date()
    
    try:
        # input_date가 문자열인 경우 datetime 객체로 변환
        if isinstance(input_date, str):
            input_date = datetime.strptime(input_date, '%Y-%m-%d').date()
        elif isinstance(input_date, datetime):
            input_date = input_date.date()
        
        # 날짜 비교 후 파일명 생성
        if input_date == today:
            return "my_log.log"
        else:
            return f"my_log.log.{input_date.strftime('%Y-%m-%d')}"
    
    except ValueError:
        return None

# Streamlit 앱 설정
st.set_page_config(
    page_title="로그 파일명 생성기",
    page_icon="📝",
    layout="wide"
)

# 페이지 제목
st.title("📝 로그 파일명 생성기")
st.markdown("---")

# 사이드바
st.sidebar.header("날짜 입력")
st.sidebar.markdown("YYYY-MM-DD 형식으로 입력해주세요")

# 오늘 날짜를 기본값으로 설정
today_str = datetime.now().strftime('%Y-%m-%d')

# 텍스트 입력
input_date = st.sidebar.text_input(
    "날짜 입력:", 
    value=today_str,
    help="예: 2024-07-29"
)

# 생성 버튼
generate_button = st.sidebar.button("파일명 생성", type="primary")

# 메인 페이지 내용
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("결과")
    
    if generate_button or input_date:
        if input_date.strip():  # 입력이 비어있지 않은 경우
            filename = generate_log_filename(input_date.strip())
            
            if filename:
                # 성공적으로 생성된 경우
                st.success("파일명이 생성되었습니다!")
                
                # 결과를 큰 글씨로 표시
                st.markdown(f"### 📄 `{filename}`")
                
                # 추가 정보 표시
                today = datetime.now().date()
                try:
                    input_date_obj = datetime.strptime(input_date.strip(), '%Y-%m-%d').date()
                    
                    if input_date_obj == today:
                        st.info("🗓️ 입력한 날짜가 오늘 날짜입니다.")
                    else:
                        diff = (today - input_date_obj).days
                        if diff > 0:
                            st.info(f"🗓️ 입력한 날짜는 {diff}일 전입니다.")
                        else:
                            st.info(f"🗓️ 입력한 날짜는 {abs(diff)}일 후입니다.")
                
                except ValueError:
                    pass
                    
            else:
                # 잘못된 날짜 형식인 경우
                st.error("❌ 올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력해주세요.")
                st.markdown("**예시:** 2024-07-29, 2024-12-25")
        else:
            st.warning("날짜를 입력해주세요.")

with col2:
    st.subheader("규칙 설명")
    st.markdown("""
    **파일명 생성 규칙:**
    
    - 🟢 **오늘 날짜**: `my_log.log`
    - 🔵 **다른 날짜**: `my_log.log.YYYY-MM-DD`
    
    **입력 형식:**
    - YYYY-MM-DD (예: 2024-07-29)
    """)
    
    # 현재 날짜 표시
    st.markdown("---")
    st.markdown(f"**오늘 날짜:** {today_str}")

# 하단에 사용 예시
st.markdown("---")
st.subheader("💡 사용 예시")

example_col1, example_col2, example_col3 = st.columns(3)

with example_col1:
    st.markdown("**오늘 날짜 입력 시:**")
    st.code("my_log.log")

with example_col2:
    st.markdown("**2024-01-15 입력 시:**")
    st.code("my_log.log.2024-01-15")

with example_col3:
    st.markdown("**2024-12-25 입력 시:**")
    st.code("my_log.log.2024-12-25")
