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
        font-size: 28px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">남양주시 AI 콘텐츠 생성기</p>', unsafe_allow_html=True)
    
    # 사이드바에 앱 선택 옵션 추가
    app_choice = st.sidebar.selectbox(
        "□ 애플리케이션 선택",
        ["보도자료 생성기", "인사말씀 생성기"]
    )
    
    # 선택된 앱 실행
    if app_choice == "보도자료 생성기":
        press_release.run()
    elif app_choice == "인사말씀 생성기":
        greeting_generator.run()

if __name__ == "__main__":
    main()