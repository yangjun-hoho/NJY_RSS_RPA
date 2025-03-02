import streamlit as st
import press_release
import greeting_generator
import document_converter  # 문서자료 대본 변환기 추가
import waste_sticker_intro  # PRA 폐기물스티커 판매정산 추가
import fax_rpa_intro  # FAX 보내기 모듈 추가
import cargo_rpa_intro  # 화물자동차 인허가 RPA 모듈 추가
import guestbook  # 방명록 모듈 추가

# 페이지 설정 - 넓은 레이아웃 적용
st.set_page_config(
    page_title="남양주시 AI & RPA 연구",
    page_icon="📝",
    layout="wide"
)

def main():
    # 메인 영역 스타일 적용
    st.markdown("""
    <style>
    .main-title {
        font-size: 38px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        margin-bottom: 1.5rem;
        text-align: left;
        background: linear-gradient(15deg, #3A0603, #D1BAB8); /* 더 연한 파란색 그라데이션 */
        color: white;
        padding: 2px 9px; /* 상하 패딩 줄임 */
        border-radius: 8px;
        box-shadow: 1px 6px 9px rgba(0, 0, 0, 0.6);
        letter-spacing: 1px;
        max-width: 800px; /* 박스 최대 너비 제한 */
        margin-left: auto; /* 좌우 중앙 정렬을 위한 마진 설정 */
        margin-right: auto;
    }
    .sidebar-text {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">남양주시 AI & RPA 연구</p>', unsafe_allow_html=True)
    
    # 사이드바에 앱 선택 옵션 추가
    st.sidebar.markdown('<p class="sidebar-text">📱 애플리케이션 선택</p>', unsafe_allow_html=True)
    app_choice = st.sidebar.selectbox(
        "",  # 레이블을 비워둠 (위에서 마크다운으로 스타일 적용)
        ["(생성형AI) 인사말씀 생성기", 
         "(생성형AI) 문서자료 대본 변환기", 
         "(생성형AI) 보도자료 생성기", 
         "(NYJ_RPA) 폐기물스티커 판매정산", 
         "(NYJ_RPA) FAX 보내기", 
         "(NYJ_RPA) 화물자동차 인허가",  # 새로운 옵션 추가
         "방명록"]
    )
    
    # 선택된 앱 실행
    if app_choice == "(생성형AI) 인사말씀 생성기":
        greeting_generator.run()
    elif app_choice == "(생성형AI) 문서자료 대본 변환기":
        document_converter.run()
    elif app_choice == "(생성형AI) 보도자료 생성기":
        press_release.run()
    elif app_choice == "(NYJ_RPA) 폐기물스티커 판매정산":
        waste_sticker_intro.run()
    elif app_choice == "(NYJ_RPA) FAX 보내기":
        fax_rpa_intro.run()
    elif app_choice == "(NYJ_RPA) 화물자동차 인허가":  # 새로운 모듈 실행 코드 추가
        cargo_rpa_intro.run()
    elif app_choice == "방명록":
        guestbook.run()

if __name__ == "__main__":
    main()