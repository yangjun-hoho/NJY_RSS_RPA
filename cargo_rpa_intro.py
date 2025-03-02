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
        st.caption("© 2025 남양주시 RPA 프로그램")

    # 스타일 및 폰트 설정
    st.markdown("""
    <style>
    .cargo-title {
        font-size: 30px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        margin-bottom: 1rem;
        text-align: left;
    }
    .sub-title {
        color: #4A88E5;
        font-size: 16px;
        margin-top: 5px;
        font-weight: 600;
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
    .step-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .step-number {
        background-color: #4A88E5;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        margin-right: 10px;
    }
    .step-title {
        font-weight: bold;
        font-size: 16px;
        color: #333;
    }
    .highlight-box {
        background-color: #e8f4f8;
        border-left: 4px solid #4A88E5;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="cargo-title">🚚 남양주시 화물자동차 인허가 RPA 프로그램</p>', unsafe_allow_html=True)
    st.caption("화물자동차 운송사업 인허가 업무 자동화 시스템")

    # 헤더 이미지
    try:
        header_image = Image.open('j001.png')
        st.image(header_image, use_container_width=True)
    except Exception as e:
        st.info("헤더 이미지(j001.png)를 불러올 수 없습니다.")

    # 프로그램 설명 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["프로그램 소개", "신청접수", "결격조회", "붙임생성기", "기술 정보"])

    # 탭 1: 프로그램 소개
    with tab1:
        st.header("프로그램 소개")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **화물자동차 인허가 RPA(Robotic Process Automation)** 프로그램은 화물자동차 운송사업 관련 인허가 업무를 자동화하여 
            행정 처리 효율성을 크게 높이기 위해 개발된 솔루션입니다.
            
            화물자동차 운송사업 관련 업무 중 특히 양수, 전입, 신규, 상속, 구조, 전출, 휴업, 폐업 등의 
            업무 처리 과정에서 반복적으로 이루어지는 작업들을 자동화하여 업무 시간을 단축하고 
            오류 가능성을 줄여줍니다.
            """)
            
            st.markdown('<p class="sub-title">주요 업무 자동화 영역</p>', unsafe_allow_html=True)
            
            st.markdown("""
            - **신청접수**: 신청인 정보, 차량정보, 허가대장 정보 등을 입력 및 저장
            - **결격조회**: 화물협회, 택시운송사업조합, 전국화물운송조합연합회, TS 운수종사자관리시스템 등 4개 사이트 일괄 조회
            - **붙임생성기**: 허가 공문, 결격조회 회신, 허가증, 심사표 등 자동 생성
            - **자동 폴더 생성**: 신청인별 문서 관리 폴더 자동 생성
            """)
        
        with col2:
            try:
                intro_img = Image.open('j002.png')
                st.image(intro_img, caption="프로그램 메인 화면", use_container_width=True)
            except Exception as e:
                st.info("이미지(j002.png)를 불러올 수 없습니다.")
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 프로그램 개발 목적

        화물자동차 운송사업 인허가 업무는 다양한 웹사이트 접속, 문서 작성, 데이터 확인 등 복잡한 절차를 포함합니다.
        이 프로그램은 이러한 반복적이고 시간 소모적인 업무를 자동화하여:

        - **업무 효율성 향상**: 처리 시간 단축 (기존 30분 → 5분 이내)
        - **휴먼 에러 방지**: 수작업 입력 과정의 오류 감소
        - **일관된 문서 생성**: 표준화된 형식의 문서 자동 생성
        - **다중 작업 처리**: 여러 사이트 동시 조회 및 작업 가능
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("시스템 요구사항")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - **운영체제**: Windows 10 이상
            - **필수 프로그램**: 
              - Microsoft Excel
              - 한글(HWP)
              - Microsoft Edge 브라우저
            """)
        
        with col2:
            st.markdown("""
            - **권장 사양**:
              - CPU: Intel i5 이상 또는 AMD 동급 사양
              - RAM: 8GB 이상
              - 하드 디스크: 100MB 이상의 여유 공간
              - 인터넷 연결: 필수
            """)

    # 탭 2: 신청접수 기능
    with tab2:
        st.header("신청접수 기능")
        
        st.markdown("""
        화물자동차 운송사업 신청 정보를 입력하고 관리하는 기능입니다. 
        신청인의 정보부터 차량 정보, 양도인 정보 등 다양한 데이터를 체계적으로 입력하고 엑셀 파일로 저장할 수 있습니다.
        """)
        
        # 신청접수 화면 이미지
        try:
            application_img = Image.open('j002.png')
            st.image(application_img, caption="신청접수 화면", use_container_width=True)
        except Exception as e:
            st.info("이미지(j002.png)를 불러올 수 없습니다.")
        
        st.markdown('<p class="sub-title">주요 입력 항목</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **신청인 정보**
            - 성명
            - 주민번호 (생년월일 자동 계산)
            - 주소
            
            **허가대장 정보**
            - 최초허가일
            - 허가번호
            - 자격증 정보
            - 근로자 정보
            - 연락처
            - 접수번호
            """)
        
        with col2:
            st.markdown("""
            **차량 정보**
            - 차량번호 (현재/이전)
            - 차명
            - 차대번호
            - 양도인 정보
            - 양도인 주민번호
            - 양도인 주소
            - 양도청 및 관할부서
            """)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<p class="feature-title">특별 기능</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **자동 데이터 계산**
            - 주민번호 입력 시 생년월일 자동 계산
            - 양도청 입력 시 관할부서 자동 검색
            - 입력필드 간 쉬운 이동(Enter 키로 다음 필드 이동)
            """)
        
        with col2:
            st.markdown("""
            **데이터 관리**
            - 엑셀 허가대장에 자동 저장
            - 작업 폴더 자동 생성 기능
            - 입력 내용 일괄 제거 기능
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("폴더 생성 기능")
        
        st.markdown("""
        신청접수 정보를 기반으로 문서 관리용 폴더를 자동으로 생성할 수 있습니다. 
        성명과 차량번호, 신청 유형에 따라 `YYMMDD_성명(차량번호)_유형` 형식으로 폴더가 생성됩니다.
        """)
        
        try:
            folder_img = Image.open('h007.png')
            st.image(folder_img, caption="폴더 생성 결과 예시", use_container_width=True)
        except Exception as e:
            st.info("이미지(h007.png)를 불러올 수 없습니다.")

    # 탭 3: 결격조회 기능
    with tab3:
        st.header("결격조회 기능")
        
        st.markdown("""
        화물자동차 운송사업 자격 취득을 위한 결격사유 조회를 자동화한 기능입니다. 
        여러 기관의 웹사이트에 자동으로 로그인하고 조회하여 업무 시간을 크게 단축해줍니다.
        """)
        
        try:
            check_img = Image.open('j003.png')
            st.image(check_img, caption="결격조회 화면", use_container_width=True)
        except Exception as e:
            st.info("이미지(j003.png)를 불러올 수 없습니다.")
        
        st.markdown('<p class="sub-title">자동 조회 사이트</p>', unsafe_allow_html=True)
        
        st.markdown("""
        프로그램은 다음 4개의 사이트에 자동으로 로그인하고 신청인 정보를 검색합니다:
        
        1. **화물협회 조회 시스템**: http://search.yongdal.or.kr
        2. **택시운송사업조합 조회 시스템**: http://pta.or.kr
        3. **전국화물운송조합연합회 조회 시스템**: http://www.kta.or.kr
        4. **TS 운수종사자관리시스템**: https://tsdms.kotsa.or.kr
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                login_img = Image.open('j006.png')
                st.image(login_img, caption="자동 로그인 과정", use_column_width=True)
            except Exception as e:
                st.info("이미지(j006.png)를 불러올 수 없습니다.")
        
        with col2:
            try:
                search_img = Image.open('j007.png')
                st.image(search_img, caption="자동 조회 과정", use_column_width=True)
            except Exception as e:
                st.info("이미지(j007.png)를 불러올 수 없습니다.")
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<p class="feature-title">결격조회 프로세스</p>', unsafe_allow_html=True)
        
        st.markdown("""
        1. **자동 로그인**: 각 사이트에 미리 설정된 계정으로 자동 로그인 진행
        2. **대상자 입력**: 조회할 대상자의 성명과 주민번호 입력
        3. **일괄 조회**: 버튼 클릭 한 번으로 모든 사이트에서 동시에 조회 진행
        4. **결과 확인**: 각 사이트에서의 조회 결과를 시각적으로 확인 가능
        5. **로그아웃**: 조회 완료 후 일괄 로그아웃 지원
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("행정정보공동이용 조회")
        
        st.markdown("""
        대상자의 개인정보를 입력하여 행정정보공동이용 시스템을 통한 조회를 지원합니다.
        경찰서 선택 옵션을 통해 남양주북부경찰서나 남양주남부경찰서 중 선택하여 조회할 수 있습니다.
        """)
        
        try:
            admin_img = Image.open('j008.png')
            st.image(admin_img, caption="행정정보공동이용 조회 화면", use_column_width=True)
        except Exception as e:
            st.info("이미지(j008.png)를 불러올 수 없습니다.")

    # 탭 4: 붙임생성기 기능
    with tab4:
        st.header("붙임생성기 기능")
        
        st.markdown("""
        화물자동차 운송사업 인허가에 필요한 각종 문서를 자동으로 생성하는 기능입니다.
        허가대장의 데이터를 활용하여 공문, 결격조회 회신, 허가증, 심사표 등을 자동으로 생성하여 시간과 노력을 크게 절약해줍니다.
        """)
        
        try:
            doc_generator_img = Image.open('j004.png')
            st.image(doc_generator_img, caption="붙임생성기 화면", use_container_width=False)
        except Exception as e:
            st.info("이미지(j004.png)를 불러올 수 없습니다.")
        
        st.markdown('<p class="sub-title">자동 생성 문서 종류</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **공문서**
            - 결격공문
            - 허가공문
            """)
            
            try:
                doc_sample1 = Image.open('j010.png')
                st.image(doc_sample1, caption="공문서 예시", use_container_width=True)
            except Exception as e:
                st.info("이미지(j010.png)를 불러올 수 없습니다.")
        
        with col2:
            st.markdown("""
            **증명서/양식**
            - 허가증
            - 양도양수심사표
            """)
            
            try:
                doc_sample2 = Image.open('j011.png')
                st.image(doc_sample2, caption="허가증/심사표 예시", use_container_width=True)
            except Exception as e:
                st.info("이미지(j011.png)를 불러올 수 없습니다.")
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<p class="feature-title">문서 생성 프로세스</p>', unsafe_allow_html=True)
        
        st.markdown("""
        1. **템플릿 및 데이터 불러오기**: 
           - 결격공문/허가공문 HWP 템플릿 선택
           - 허가대장 엑셀 파일 불러오기
           - 저장할 폴더 선택
        
        2. **연번 지정**: 허가대장에서 문서를 생성할 행의 연번 지정
        
        3. **문서 생성**:
           - 결격공문 생성: 결격조회 관련 HWP 문서 자동 생성
           - 허가공문 생성: 허가 관련 HWP 문서 자동 생성
           - 허가증 생성: 개인화물운송사업허가증 PDF 생성
           - 심사표 생성: 양도양수심사확인표 PDF 생성
        
        4. **자동 저장 및 열기**:
           - 지정된 폴더에 '[문서종류]_[신청인명].확장자' 형식으로 저장
           - 생성된 문서 자동 열기
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("데이터 필드 자동 매핑")
        
        st.markdown("""
        프로그램은 허가대장 엑셀 파일의 데이터를 문서 템플릿의 필드에 자동으로 매핑합니다.
        주요 매핑 필드는 다음과 같습니다:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - 양도청/관할부서
            - 민원접수번호
            - 양도인/양도인주민번호/양도인주사무소
            - 차량번호(현재/이전)
            - 허가번호(현재/이전)
            """)
        
        with col2:
            st.markdown("""
            - 신청인 성명/주민번호/주소
            - 차대번호
            - 세무서/경찰서
            - 담당자 이름
            - 결격회신 정보
            """)
        
        try:
            mapping_img = Image.open('j012.png')
            st.image(mapping_img, caption="데이터 필드 매핑 예시", use_column_width=True)
        except Exception as e:
            st.info("이미지(j012.png)를 불러올 수 없습니다.")

    # 탭 5: 기술 정보
    with tab5:
        st.header("기술 정보")
        
        st.markdown("""
        화물자동차 인허가 RPA 프로그램은 다양한 기술과 라이브러리를 활용하여 개발되었습니다.
        주요 기술적 특징과 아키텍처에 대한 정보입니다.
        """)
        
        st.markdown('<p class="sub-title">사용 기술 및 라이브러리</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **UI 구현**
            - Tkinter/CustomTkinter: 그래픽 사용자 인터페이스
            - ttk: 테마 적용 위젯
            
            **데이터 처리**
            - Pandas: 엑셀 데이터 분석 및 처리
            - Openpyxl: 엑셀 파일 읽기/쓰기
            """)
        
        with col2:
            st.markdown("""
            **자동화 기술**
            - Playwright: 브라우저 자동화
            - Win32COM: 한글(HWP), 엑셀 자동화
            
            **기타 기능**
            - keyboard: 키보드 입력 자동화
            - pyperclip: 클립보드 제어
            - datetime: 날짜 처리
            """)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<p class="feature-title">아키텍처 구성</p>', unsafe_allow_html=True)
        
        st.markdown("""
        프로그램은 크게 4개의 모듈로 구성되어 있습니다:
        
        1. **UI 모듈**: Tkinter 기반 사용자 인터페이스 제공
        2. **데이터 처리 모듈**: 엑셀 파일 및 입력 데이터 처리
        3. **자동화 모듈**: 웹 브라우저 및 문서 자동화 처리
        4. **유틸리티 모듈**: 보조 기능(폴더 생성, 파일 저장 등) 제공
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("개발 및 유지보수 정보")
        
        st.markdown("""
        - **개발 시기**: 2024년
        - **개발 언어**: Python 3.9
        - **라이센스**: 남양주시 내부용
        """)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 지원 및 문의
        
        프로그램 사용 중 문제가 발생하거나 추가 문의사항이 있으면 아래 연락처로 문의해주세요.
        
        - **이메일**: hoho4348@korea.kr
        - **전화**: 031-590-2428
        - **담당부서**: 남양주시 교통행정과
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # 페이지 푸터
    st.divider()
    st.caption("© 2025 남양주시 화물자동차 인허가 RPA 프로그램 | 모든 권리 보유")

if __name__ == "__main__":
    run()