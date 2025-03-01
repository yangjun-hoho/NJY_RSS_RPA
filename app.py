import streamlit as st
import press_release
import greeting_generator

# 페이지 설정 - 넓은 레이아웃 적용
st.set_page_config(
    page_title="남양주시 AI 콘텐츠 생성기",
    page_icon="📝",
    layout="wide"
)

def main():
    # 메인 영역 스타일 적용
    st.markdown("""
    <style>
    .main-title {
        font-size: 40px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        font-weight: 800;
        color: #555;
        font-size: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    /* selectbox 화살표 숨기기 */
    div[data-baseweb="select"] > div {
        box-shadow: none !important;
        background-image: none !important;
    }
    /* selectbox 테두리 제거 */
    div[role="listbox"] ul {
        border: none !important;
    }
    /* 선택 항목 색상 변경 */
    .stSelectbox [data-baseweb="select"] {
        border: none !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">남양주시 AI 콘텐츠 생성기</p>', unsafe_allow_html=True)
    
    # 앱 옵션들 정의 
    app_options = ["AI 인사말씀 생성기", "AI 보도자료 생성기"]
    
    # 사이드바에 앱 선택 옵션 추가 (selectbox를 텍스트처럼 보이게 함)
    st.sidebar.markdown("## 📱 애플리케이션 선택")
    
    # 선택 상자를 사용하지만 텍스트처럼 보이게 스타일링
    app_choice = st.sidebar.selectbox(
        "",
        app_options,
        label_visibility="collapsed"  # 라벨 숨기기
    )
    
    # 선택된 앱 실행
    if app_choice == "AI 인사말씀 생성기":
        greeting_generator.run()
    elif app_choice == "AI 보도자료 생성기":
        press_release.run()

if __name__ == "__main__":
    main()