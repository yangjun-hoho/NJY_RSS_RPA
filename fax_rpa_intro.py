import streamlit as st
from PIL import Image
import base64
from io import BytesIO

def run():
    # 사이드바 설정
    with st.sidebar:
        st.divider()
        # AI 모델 선택
        model_provider = st.radio(
            "🤖 AI모델 선택",
            ["OpenAI GPT-4o", "Google Gemini-2.0"]
        )
        
        # 공통 설정
        temperature = st.slider("⚙️ 창의성 수준", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        
        st.divider()
        st.caption("© 2025 남양주시 RPA프로그램")

    # 페이지 헤더 수정 - 타이틀과 이모지 변경, 폰트 크기 조정

    # 스타일 및 폰트 설정
    st.markdown("""
    <style>
    .fax-title {
        font-size: 30px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        margin-bottom: 1rem;
        text-align: left;
    }
    .sub-title {
        color: white;
        font-size: 16px;
        margin-top: 5px;
    }
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #4A88E5;
    }
    .feature-title {
        font-weight: bold;
        color: #4A88E5;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .feature-desc {
        color: #333;
    }
    .code-block {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="fax-title">📠 남양주 WebFax RPA 프로그램</p>', unsafe_allow_html=True)
    st.caption("남양주시 웹팩스 자동전송 프로그램")

    header_image = Image.open('f001.png')
    st.image(header_image, use_container_width=True)

    # 프로그램 설명 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["프로그램 소개", "주요 기능", "사용 방법", "기술 정보"])

    # 탭 1: 프로그램 소개
    with tab1:
        st.header("프로그램 소개")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **남양주 WebFax RPA(Robotic Process Automation) 프로그램**은 팩스 전송 작업을 자동화하기 위해 개발된 솔루션입니다.
            
            이 프로그램은 다음과 같은 특징을 가지고 있습니다:
            
            - **자동 웹 로그인**: 남양주시 웹팩스 시스템에 자동으로 로그인합니다.
            - **정보 자동 입력**: 미리 저장된 제목, 수신처, 연락처 정보를 자동으로 입력합니다.
            - **PDF 파일 자동 첨부**: 지정된 폴더의 PDF 파일을 자동으로 첨부합니다.
            - **사용자 친화적 인터페이스**: 직관적인 GUI로 누구나 쉽게 사용할 수 있습니다.
            - **정보 저장 기능**: 자주 사용하는 로그인 정보와 팩스 수신처 정보를 저장할 수 있습니다.
            
            이 프로그램을 통해 반복적인 팩스 전송 업무를 간소화하고, 업무 효율성을 크게 향상시킬 수 있습니다.
            """)
        
        with col2:
            # 프로그램 스크린샷 또는 아이콘 이미지
            try:
                fax_img = Image.open('fax_screenshot.png')
                st.image(fax_img, caption="프로그램 실행 화면", use_column_width=True)
            except:
                # 이미지 파일이 없는 경우 아이콘 표시
                st.markdown("""
                <div style="text-align: center; font-size: 80px; color: #4A88E5; margin: 20px 0;">
                <i class="fas fa-fax"></i> 📠
                </div>
                <p style="text-align: center;">WebFax RPA 프로그램</p>
                """, unsafe_allow_html=True)

    # 탭 2: 주요 기능
    with tab2:
        st.header("주요 기능")
        
        features = [
            {
                "title": "웹팩스 시스템 자동 로그인",
                "description": "저장된 계정 정보를 사용하여 남양주시 웹팩스 시스템에 자동으로 로그인합니다. 매번 로그인할 필요 없이 프로그램 실행 후 로그인 버튼 한 번으로 시스템에 접속합니다.",
                "icon": "🔑"
            },
            {
                "title": "팩스 정보 자동 입력",
                "description": "자주 사용하는 팩스 제목, 수신처 이름, 팩스 번호를 미리 저장하고 선택만으로 자동 입력할 수 있습니다. 최대 3개의 팩스 수신처 정보를 저장하고 선택적으로 사용할 수 있습니다.",
                "icon": "📝"
            },
            {
                "title": "PDF 파일 자동 첨부",
                "description": "특정 폴더(D:\\팩스파일)에 저장된 모든 PDF 파일을 자동으로 찾아서 팩스 첨부 파일로 추가합니다. 여러 파일을 한 번에 처리할 수 있어 효율적입니다.",
                "icon": "📎"
            },
            {
                "title": "설정 자동 저장",
                "description": "자주 사용하는 계정 정보와 팩스 수신처 정보를 INI 파일에 저장하여 프로그램 재실행 시에도 동일한 정보를 사용할 수 있습니다. 저장 체크박스로 저장 여부를 선택할 수 있습니다.",
                "icon": "💾"
            }
        ]
        
        for feature in features:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-title">{feature['icon']} {feature['title']}</div>
                <div class="feature-desc">{feature['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 탭 3: 사용 방법
    with tab3:
        st.header("사용 방법")
        
        st.subheader("1. 프로그램 설치 및 준비")
        st.markdown("""
        1. 프로그램 실행 파일을 다운로드하여 컴퓨터에 설치합니다.
        2. `D:\팩스파일` 폴더를 생성합니다. (없을 경우)
        3. 전송할 PDF 파일을 `D:\팩스파일` 폴더에 복사합니다.
        """)
        
        st.subheader("2. 프로그램 실행 및 로그인")
        st.markdown("""
        1. 프로그램을 실행합니다.
        2. 아이디와 비밀번호를 입력합니다.
        3. 로그인 정보를 저장하려면 "로그인 정보 저장" 체크박스를 선택합니다.
        4. "로그인" 버튼을 클릭하여 웹팩스 시스템에 접속합니다.
        """)
        
        st.subheader("3. 팩스 정보 입력 및 전송")
        st.markdown("""
        1. 좌측 라디오 버튼을 선택하여 사용할 팩스 정보 행을 선택합니다.
        2. 제목, 수신처, 연락처를 입력합니다. (저장된 정보가 있다면 자동으로 표시됩니다)
        3. 정보를 저장하려면 "저장" 체크박스를 선택합니다.
        4. "입력" 버튼을 클릭하여 팩스 전송 과정을 시작합니다.
        5. 프로그램이 자동으로 웹팩스 시스템에 정보를 입력하고 파일을 첨부합니다.
        """)
        
        st.info('📍 주의: 프로그램 실행 중에는 브라우저 창을 닫거나 조작하지 마세요. 자동화 과정이 중단될 수 있습니다.')

    # 탭 4: 기술 정보
    with tab4:
        st.header("기술 정보")
        
        st.subheader("사용된 기술")
        st.markdown("""
        - **CustomTkinter**: 현대적인 GUI 인터페이스를 제공하는 Tkinter 확장 라이브러리
        - **Playwright**: Microsoft에서 개발한 브라우저 자동화 라이브러리
        - **asyncio**: 비동기 I/O 처리를 위한 Python 표준 라이브러리
        - **configparser**: 설정 파일 처리를 위한 라이브러리
        """)
        
        st.subheader("시스템 요구 사항")
        st.markdown("""
        - **운영체제**: Windows 10 이상
        - **브라우저**: Microsoft Edge (자동으로 실행됨)
        - **Python**: 3.7 이상 (실행 파일 사용 시 필요 없음)
        - **디스크 공간**: 100MB 이상의 여유 공간
        - **인터넷 연결**: 웹팩스 시스템 접속을 위한 인터넷 연결 필요
        """)
        
        st.subheader("주요 코드 스니펫")
        st.markdown("팩스 자동 전송 함수 예시:")
        st.code("""
async def async_send_fax(subject, recipient, fax_number):
    # 메뉴 클릭
    await page.click('#sub_menu_img_01_01')
    
    # 입력 필드 작성
    await page.fill('#txt_subject', subject)
    await page.fill('#txt_recv_name', recipient)
    await page.fill('#txt_recv_faxno', fax_number)
    
    # 수신자 추가
    await page.click('#btn_recv_add')
    
    # PDF 파일 업로드
    pdf_folder_path = r"D:\\팩스파일"
    pdf_files = [os.path.join(pdf_folder_path, f) 
                for f in os.listdir(pdf_folder_path) 
                if f.endswith('.pdf')]
    
    # 파일 업로드 로직...
        """, language="python")

    # 푸터 섹션
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("© 2025 남양주시 RPA 자동화 시스템")
    
    with col2:
        st.caption("문의: hoho4348@korea.kr / 031-590-2428")

if __name__ == "__main__":
    run()