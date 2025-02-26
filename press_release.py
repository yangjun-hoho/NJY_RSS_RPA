import streamlit as st
import openai
from openai import OpenAI
import google.generativeai as genai
from datetime import datetime

def run():
    # API 키 (환경 변수에서 로드)
    import os
    from dotenv import load_dotenv
    
    # .env 파일 로드
    load_dotenv()
    
    # 환경 변수에서 API 키 가져오기
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # API 키 확인
    if not OPENAI_API_KEY or not GEMINI_API_KEY:
        st.error("API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY와 GEMINI_API_KEY를 설정해주세요.")
        st.stop()

    # 사이드바 설정
    with st.sidebar:
        st.title("📝 AI 보도자료 생성기")
        
        # AI 모델 선택
        model_provider = st.radio(
            "□ AI모델 선택",
            ["OpenAI GPT", "Google Gemini"]
        )
        
        # 공통 설정
        temperature = st.slider("□ 창의성 수준", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        
        st.divider()
        st.caption("© 2025 남양주시 AI 보도자료 생성기")

    # 메인 영역 스타일 적용
    st.markdown("""
    <style>
    .press-release {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    .press-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    .press-content {
        font-size: 14px;
        line-height: 1.5;
    }
    .title-option {
        background-color: #f0f7ff;
        border-radius: 5px;
        padding: 8px;
        margin-bottom: 8px;
    }
    .keyword-box {
        margin-bottom: 4px;
    }
    h1 {
        font-size: 24px !important;
    }
    h2 {
        font-size: 18px !important;
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }
    h3 {
        font-size: 16px !important;
        margin-top: 8px !important;
        margin-bottom: 4px !important;
    }
    .stTextArea textarea {
        max-height: 100px;
        min-height: 50px;
    }

    /* 마크다운 헤더와 텍스트 영역 사이 간격 조정 */
    h5 {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }

    .stTextArea {
        margin-top: -10px !important;
        padding-top: 0px !important;
    }

    .element-container {
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if "core_content" not in st.session_state:
        st.session_state.core_content = ""
    if "keywords" not in st.session_state:
        st.session_state.keywords = ["", "", "", "", ""]
    if "titles" not in st.session_state:
        st.session_state.titles = []
    if "selected_title" not in st.session_state:
        st.session_state.selected_title = ""
    if "press_release" not in st.session_state:
        st.session_state.press_release = ""

    # OpenAI GPT API 호출 함수 - 제목 생성
    def generate_titles_with_openai(core_content, keywords, temperature):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 키워드 문자열 생성
        keywords_str = ", ".join([k for k in keywords if k.strip()])
        
        prompt = f"""
        핵심 내용: {core_content}
        키워드: {keywords_str}
        
        위 내용을 바탕으로 눈길을 끄는 창의적인 보도자료 제목 3개를 생성해주세요. 
        각 제목은 번호를 붙여서 구분해주세요(1., 2., 3.).
        제목은 간결하고 임팩트 있게 작성해주세요.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        return parse_titles(response.choices[0].message.content)

    # Gemini API 호출 함수 - 제목 생성
    def generate_titles_with_gemini(core_content, keywords, temperature):
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 키워드 문자열 생성
        keywords_str = ", ".join([k for k in keywords if k.strip()])
        
        prompt = f"""
        핵심 내용: {core_content}
        키워드: {keywords_str}
        
        위 내용을 바탕으로 눈길을 끄는 창의적인 보도자료 제목 3개를 생성해주세요. 
        각 제목은 번호를 붙여서 구분해주세요(1., 2., 3.).
        제목은 간결하고 임팩트 있게 작성해주세요.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                    generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        return parse_titles(response.text)

    # 제목 파싱 함수
    def parse_titles(text):
        lines = text.strip().split('\n')
        titles = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                title = line[2:].strip()
                titles.append(title)
        
        # 3개를 채우지 못했다면 추가
        while len(titles) < 3:
            titles.append(f"제목 옵션 {len(titles)+1}")
            
        return titles[:3]  # 최대 3개까지만 반환

    # OpenAI GPT API 호출 함수 - 보도자료 생성
    def generate_press_release_with_openai(title, core_content, keywords, temperature):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 키워드 문자열 생성
        keywords_str = ", ".join([k for k in keywords if k.strip()])
        
        prompt = f"""
        제목: {title}
        핵심 내용: {core_content}
        키워드: {keywords_str}
        
        위 정보를 바탕으로 전문적이고 공식적인 느낌의 보도자료를 작성해주세요.
        보도자료는 선택된 제목, 내용으로 구성되어야 합니다.
        내용은 도입부, 본문, 마무리 문단으로 자연스럽게 구성해주세요.
        전체적으로 500-800자 정도로 작성해주세요.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        return response.choices[0].message.content

    # Gemini API 호출 함수 - 보도자료 생성
    def generate_press_release_with_gemini(title, core_content, keywords, temperature):
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 키워드 문자열 생성
        keywords_str = ", ".join([k for k in keywords if k.strip()])
        
        prompt = f"""
        제목: {title}
        핵심 내용: {core_content}
        키워드: {keywords_str}
        
        위 정보를 바탕으로 전문적이고 공식적인 느낌의 보도자료를 작성해주세요.
        보도자료는 선택된 제목, 내용으로 구성되어야 합니다.
        내용은 도입부, 본문, 마무리 문단으로 자연스럽게 구성해주세요.
        전체적으로 500-800자 정도로 작성해주세요.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                    generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        return response.text

    # 메인 레이아웃
    st.title("AI 보도자료 생성기")
    st.caption("핵심 내용과 키워드를 입력하고, AI가 보도자료를 생성해드립니다.")

    # 좌우 컬럼 생성
    left_col, right_col = st.columns([1, 1])

    # 좌측 컬럼 - 입력 영역
    with left_col:
        st.subheader("< 입력 >")
        # 핵심 내용 입력
        st.markdown("##### 핵심 내용")
        core_content = st.text_area("", 
                                value=st.session_state.core_content,
                                height=120,
                                placeholder="보도자료에 포함할 핵심 내용을 입력하세요")

        # 키워드 입력
        st.markdown("##### 키워드 (최대 5개)")
        
        # 2개의 하위 컬럼으로 키워드 입력 필드 배치
        kw_col1, kw_col2 = st.columns(2)
        
        with kw_col1:
            for i in range(3):
                st.session_state.keywords[i] = st.text_input(f"키워드 {i+1}", 
                                                        value=st.session_state.keywords[i],
                                                        key=f"keyword_{i}",
                                                        label_visibility="collapsed",
                                                        placeholder=f"키워드 {i+1}")

        with kw_col2:
            for i in range(3, 5):
                st.session_state.keywords[i] = st.text_input(f"키워드 {i+1}", 
                                                        value=st.session_state.keywords[i],
                                                        key=f"keyword_{i}",
                                                        label_visibility="collapsed",
                                                        placeholder=f"키워드 {i+1}")

        # 핵심 내용과 키워드 저장
        st.session_state.core_content = core_content
        

    # 우측 컬럼 - 결과 출력 영역
    with right_col:
        st.subheader("< 결과 >")
        # 제목 생성 버튼
        if st.button("제목 생성하기", type="primary"):
            with st.spinner("창의적인 제목을 생성하고 있습니다..."):
                try:
                    if model_provider == "OpenAI GPT":
                        st.session_state.titles = generate_titles_with_openai(
                            core_content, 
                            st.session_state.keywords,
                            temperature
                        )
                    else:  # Google Gemini
                        st.session_state.titles = generate_titles_with_gemini(
                            core_content, 
                            st.session_state.keywords,
                            temperature
                        )
                    
                    # 첫 번째 제목을 기본 선택
                    st.session_state.selected_title = st.session_state.titles[0]
                    
                except Exception as e:
                    st.error(f"제목 생성 중 오류가 발생했습니다: {str(e)}")

        
        # 제목 옵션 표시 영역
        title_container = st.container()
        with title_container:
            if st.session_state.titles:
                st.markdown("##### 제목 선택")
                
                selected_title = st.radio(
                    "",
                    st.session_state.titles,
                    index=st.session_state.titles.index(st.session_state.selected_title) if st.session_state.selected_title in st.session_state.titles else 0,
                    label_visibility="collapsed"
                )
                
                # 선택된 제목 저장
                st.session_state.selected_title = selected_title
                
                # 보도자료 생성 버튼
                if st.button("보도자료 생성하기", type="primary"):
                    with st.spinner("보도자료를 생성하고 있습니다..."):
                        try:
                            if model_provider == "OpenAI GPT":
                                st.session_state.press_release = generate_press_release_with_openai(
                                    st.session_state.selected_title,
                                    core_content,
                                    st.session_state.keywords,
                                    temperature
                                )
                            else:  # Google Gemini
                                st.session_state.press_release = generate_press_release_with_gemini(
                                    st.session_state.selected_title,
                                    core_content,
                                    st.session_state.keywords,
                                    temperature
                                )
                        except Exception as e:
                            st.error(f"보도자료 생성 중 오류가 발생했습니다: {str(e)}")

        # 보도자료 표시 영역
        press_release_container = st.container()
        with press_release_container:
            if st.session_state.press_release:
                st.markdown("##### 생성된 보도자료")
                
                st.markdown(f"""
                <div class="press-release">
                    <div class="press-content">
                        {st.session_state.press_release}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 버튼 행 (복사 및 새로 만들기)
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    if st.button("텍스트 복사", type="secondary"):
                        st.markdown(f"""
                        <script>
                        navigator.clipboard.writeText(`{st.session_state.press_release.replace("`", "\\`")}`);
                        </script>
                        """, unsafe_allow_html=True)
                        st.success("클립보드에 복사되었습니다!")
                
                with btn_col2:
                    if st.button("새 보도자료 작성"):
                        st.session_state.core_content = ""
                        st.session_state.keywords = ["", "", "", "", ""]
                        st.session_state.titles = []
                        st.session_state.selected_title = ""
                        st.session_state.press_release = ""
                        st.rerun()