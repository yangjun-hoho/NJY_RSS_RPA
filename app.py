import streamlit as st

# 페이지 설정을 가장 먼저 실행 - 다른 모듈 import 전에 설정
st.set_page_config(
    page_title="남양주시 AI & RPA 연구",
    page_icon="📝",
    layout="wide"
)

# 나머지 모듈 import
import press_release
import greeting_generator
import document_converter
import waste_sticker_intro
import fax_rpa_intro
import cargo_rpa_intro
import guestbook
import tts_generator
import ppt_generator
import excel_formatter  # 엑셀 정리 모듈 import
import report_generator  # 보고서/계획서 생성기 모듈 import
from usage_counter import count_app_usage, admin_stats_page

# 관리자 인증 함수
def authenticate_admin():
    # 세션 상태 초기화
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    # 이미 인증된 경우 바로 True 반환
    if st.session_state.admin_authenticated:
        return True
    
    # 인증 UI
    st.title("관리자 인증")
    
    # 관리자 비밀번호 - 실제 구현시 보안 강화 필요
    ADMIN_PASSWORD = "203843"  # 실제 사용시 더 강력한 비밀번호 사용 권장
    
    password = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    if st.button("인증"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.success("인증 성공! 통계 페이지로 이동합니다.")
            return True
        else:
            st.error("비밀번호가 일치하지 않습니다.")
            return False
    
    return False

def main():
    # 메인 영역 스타일 적용
    st.markdown("""
    <style>
    .main-title {
        font-size: 28px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        margin-bottom: -1rem;
        text-align: left;
        background: linear-gradient(15deg, #3A0603, #D1BAB8);
        color: white;
        padding: 2px 9px;
        border-radius: 10px;
        box-shadow: 1px 6px 9px rgba(0, 0, 0, 0.6);
        letter-spacing: 1px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    .sidebar-text {
        font-weight: bold;
        margin-bottom: -2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바에 앱 선택 옵션 추가
    st.sidebar.markdown('<p class="sidebar-text">📱 애플리케이션 선택</p>', unsafe_allow_html=True)
    app_choice = st.sidebar.selectbox(
        "",
        ["(생성형AI) 인사말씀 생성기", 
         "(생성형AI) 문서자료 대본 변환기", 
         "(생성형AI) 보도자료 생성기", 
         "(생성형AI) TTS 음성 변환기",
         "(생성형AI) 문서 PPT 변환기", 
         "(생성형AI) 엑셀 정리하기",
         "(생성형AI) 보고서/계획서 생성기",  # 보고서/계획서 생성기 메뉴 추가
         "(NYJ_RPA) 폐기물스티커 판매정산", 
         "(NYJ_RPA) FAX 보내기", 
         "(NYJ_RPA) 화물자동차 인허가",
         "방명록",
         "관리자"]
    )
    
    # 메인 타이틀은 관리자가 아닐 때만 표시
    if app_choice != "관리자":
        st.markdown('<p class="main-title">남양주 AI & RPA(Robotic Process Automation)</p>', unsafe_allow_html=True)
    
    # 선택된 앱 실행
    if app_choice == "(생성형AI) 인사말씀 생성기":
        count_app_usage("인사말씀 생성기")
        greeting_generator.run()
        
    elif app_choice == "(생성형AI) 문서자료 대본 변환기":
        count_app_usage("문서자료 대본 변환기")
        document_converter.run()
        
    elif app_choice == "(생성형AI) 보도자료 생성기":
        count_app_usage("보도자료 생성기")
        press_release.run()
        
    elif app_choice == "(생성형AI) TTS 음성 변환기":
        count_app_usage("TTS 음성 변환기")
        tts_generator.run()
    
    elif app_choice == "(생성형AI) 문서 PPT 변환기":
        count_app_usage("문서 PPT 변환기")
        ppt_generator.run()
        
    elif app_choice == "(생성형AI) 엑셀 정리하기":
        count_app_usage("엑셀 정리하기")
        excel_formatter.run()
    
    elif app_choice == "(생성형AI) 보고서/계획서 생성기":
        count_app_usage("보고서/계획서 생성기")
        report_generator.run()
        
    elif app_choice == "(NYJ_RPA) 폐기물스티커 판매정산":
        count_app_usage("폐기물스티커 판매정산")
        waste_sticker_intro.run()
        
    elif app_choice == "(NYJ_RPA) FAX 보내기":
        count_app_usage("FAX 보내기")
        fax_rpa_intro.run()
        
    elif app_choice == "(NYJ_RPA) 화물자동차 인허가":
        count_app_usage("화물자동차 인허가")
        cargo_rpa_intro.run()
        
    elif app_choice == "방명록":
        count_app_usage("방명록")
        guestbook.run()
        
    elif app_choice == "관리자":
        count_app_usage("관리자")
        
        # 관리자 인증 성공 시에만 통계 페이지 표시
        if authenticate_admin():
            admin_stats_page()

if __name__ == "__main__":
    main()