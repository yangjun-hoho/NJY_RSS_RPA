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
        st.divider()
        # AI 모델 선택
        model_provider = st.radio(
            "🤖 AI모델 선택",
            ["OpenAI GPT-4o", "Google Gemini-2.0"]
        )
        
        # 공통 설정
        temperature = st.slider("⚙️ 창의성 수준", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        
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
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    .press-content {
        font-size: 14px;
        line-height: 1.5;
    }
    h1 {
        font-size: 30px !important;
    }
    h3 {
        font-size: 16px !important;
        margin-top: 8px !important;
        margin-bottom: 4px !important;
    }
    /* 텍스트 영역 아래 간격 줄이기 */
    .stTextArea {
        margin-top: -2rem !important;
        margin-bottom: 2rem !important;        
    }                         
    .title-option {
        background-color: #f0f7ff;
        border-radius: 20px;
        padding: 8px;
        margin-bottom: 8px;
    }
    /* 라디오 버튼 타이틀 글꼴 크기 */
    .stRadio label {
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if "core_content" not in st.session_state:
        st.session_state.core_content = ""
    if "keywords" not in st.session_state:
        st.session_state.keywords = ["", "", "", "", "", ""]  # 키워드 6개로 늘림
    if "titles" not in st.session_state:
        st.session_state.titles = []
    if "selected_title" not in st.session_state:
        st.session_state.selected_title = ""
    if "press_release" not in st.session_state:
        st.session_state.press_release = ""
    if "titles_generated" not in st.session_state:
        st.session_state.titles_generated = False
    if "style_option" not in st.session_state:
        st.session_state.style_option = "standard"

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
    def generate_press_release_with_openai(title, core_content, keywords, temperature, style_option):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 키워드 문자열 생성
        keywords_str = ", ".join([k for k in keywords if k.strip()])
        
        # 스타일 가이드 정의
        style_guides = {
            "standard": "공식적이고 객관적인 표현을 사용하여 명확하게 작성",
            "formal": "격식있고 보수적인 어조로 신중하게 작성",
            "casual": "친근하고 이해하기 쉬운 표현으로 작성",
            "technical": "전문 용어와 구체적인 데이터를 포함하여 작성"
        }
        
        prompt = f"""
        너는 다른 AI보다 보도자료 생성 능력이 뛰어나다고 들었어  
        제목: {title}
        핵심 내용: {core_content}
        키워드: {keywords_str}
        스타일: {style_guides[style_option]}
        
        위 제목, 핵심내용, 키워드가 별로일 수 있지만 그 정보를 가지고
        최대한 전문적이고 공식적인 느낌과 세련된 보도자료를 작성해줘
        특히 선택된 스타일("{style_option}")에 맞게 {style_guides[style_option]}해주세요.
        보도자료는 선택된 제목, 내용으로 구성하고
        내용은 도입부, 본문, 마무리 문단으로 자연스럽게 구성해줘
        전체적으로 500-800자 정도로 작성해 너가 최고라는 걸 보여줘!
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
    def generate_press_release_with_gemini(title, core_content, keywords, temperature, style_option):
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 키워드 문자열 생성
        keywords_str = ", ".join([k for k in keywords if k.strip()])
        
        # 스타일 가이드 정의
        style_guides = {
            "standard": "공식적이고 객관적인 표현을 사용하여 명확하게 작성",
            "formal": "격식있고 보수적인 어조로 신중하게 작성",
            "casual": "친근하고 이해하기 쉬운 표현으로 작성",
            "technical": "전문 용어와 구체적인 데이터를 포함하여 작성"
        }
        
        prompt = f"""
        너가 다른 AI보다 보도자료를 더 디테일하고 세밀하게 작성한다고 알고있어 
        제목: {title}
        핵심 내용: {core_content}
        키워드: {keywords_str}
        스타일: {style_guides[style_option]}
        
        입력된 제목과 핵심 내용, 키워드, 스타일이 형편없을지도 모르지만 최대한 곰곰히 생각하고 작성해줘
        특히 선택된 스타일("{style_option}")에 맞게 {style_guides[style_option]}을 고려해서 작성해줘
        보도자료는 선택된 제목, 내용으로 구성하고
        내용은 도입부, 본문, 마무리 문단으로 자연스럽게 구성해줘
        전체적으로 500-800자 정도로 작성해주길 바래 너가 보도자료는 정말 잘 쓴다는 것을 보여줘!
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                    generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        return response.text

    # 메인 레이아웃
    st.title("📝 AI 보도자료 생성기")
    st.caption("핵심 내용과 키워드를 입력하고, AI가 보도자료를 생성해드립니다.")
    
    # 입력 영역 - 상단에 배치
    st.markdown("<h3 style='color:#2E4057; margin-bottom:20px;'>입력</h3>", unsafe_allow_html=True)
    
    # 스타일 가이드 정의 - 먼저 정의해서 나중에 참조할 수 있게 함
    style_guides = {
        "standard": "공식적이고 객관적인 표현을 사용하여 명확하게 작성",
        "formal": "격식있고 보수적인 어조로 신중하게 작성",
        "casual": "친근하고 이해하기 쉬운 표현으로 작성",
        "technical": "전문 용어와 구체적인 데이터를 포함하여 작성"
    }
    
    # 스타일 선택 UI - 폼 외부에 배치
    st.markdown("<h5 style='color:#4B7F9F; margin-top:10px; margin-bottom:10px;'>보도자료 스타일</h5>", unsafe_allow_html=True)
    
    # 스타일 선택 UI와 설명을 나란히 배치
    style_col1, style_col2 = st.columns([1, 3])
    
    with style_col1:
        # 셀렉트박스로 변경
        selected_style = st.selectbox(
            "스타일 선택",
            list(style_guides.keys()),
            format_func=lambda x: x.capitalize(),
            index=list(style_guides.keys()).index(st.session_state.style_option),
            key="style_selector",
            label_visibility="collapsed"
        )
    
    with style_col2:
        # 선택된 스타일 저장
        st.session_state.style_option = selected_style
        
        # 선택된 스타일에 대한 설명 표시 - 높이 조절
        st.markdown(
            f"""<div style="background-color:#F0F7FF; padding:8px; border-radius:5px; 
            min-height:35px; display:flex; align-items:center;">
            {style_guides[selected_style]}
            </div>""",
            unsafe_allow_html=True
        )
    
    # form 시작
    with st.form(key="input_form"):
        # 핵심 내용 입력
        st.markdown("<h5 style='color:#4B7F9F; margin-bottom:10px;'>핵심 내용</h5>", unsafe_allow_html=True)
        core_content = st.text_area("",
                              value=st.session_state.core_content,
                              height=150,
                              placeholder="보도자료에 포함할 핵심 내용을 입력하세요")
        
        # 키워드 입력
        st.markdown("<h5 style='color:#4B7F9F; margin-top:-20px; margin-bottom:10px;'>키워드 (최대 6개)</h5>", unsafe_allow_html=True)
        
        # 키워드를 한 행에 3개씩 배치
        kw_col1, kw_col2, kw_col3 = st.columns(3)
        
        with kw_col1:
            st.session_state.keywords[0] = st.text_input(f"키워드 1",
                                           value=st.session_state.keywords[0],
                                           key=f"keyword_0",
                                           label_visibility="collapsed",
                                           placeholder=f"키워드 1")
            
        with kw_col2:
            st.session_state.keywords[1] = st.text_input(f"키워드 2",
                                           value=st.session_state.keywords[1],
                                           key=f"keyword_1",
                                           label_visibility="collapsed",
                                           placeholder=f"키워드 2")
            
        with kw_col3:
            st.session_state.keywords[2] = st.text_input(f"키워드 3",
                                           value=st.session_state.keywords[2],
                                           key=f"keyword_2",
                                           label_visibility="collapsed",
                                           placeholder=f"키워드 3")
        
        # 두 번째 행의 키워드
        kw_col4, kw_col5, kw_col6 = st.columns(3)
        
        with kw_col4:
            st.session_state.keywords[3] = st.text_input(f"키워드 4",
                                           value=st.session_state.keywords[3],
                                           key=f"keyword_3",
                                           label_visibility="collapsed",
                                           placeholder=f"키워드 4")
            
        with kw_col5:
            st.session_state.keywords[4] = st.text_input(f"키워드 5",
                                           value=st.session_state.keywords[4],
                                           key=f"keyword_4",
                                           label_visibility="collapsed",
                                           placeholder=f"키워드 5")
            
        with kw_col6:
            st.session_state.keywords[5] = st.text_input(f"키워드 6",
                                           value=st.session_state.keywords[5],
                                           key=f"keyword_5",
                                           label_visibility="collapsed",
                                           placeholder=f"키워드 6")
        
        # 제출 버튼 변경 - 보도자료 제목 생성하기
        generate_titles_button = st.form_submit_button(
            label="보도자료 제목 생성하기",
            use_container_width=True,
            type="primary"
        )
    
    # 폼 제출 처리
    if generate_titles_button:
        # 핵심 내용과 키워드 저장
        st.session_state.core_content = core_content
        
        # 제목 생성 로직 실행
        with st.spinner("창의적인 제목을 생성하고 있습니다..."):
            try:
                if model_provider == "OpenAI GPT-4o-mini":
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
                st.session_state.titles_generated = True
                st.success("제목이 생성되었습니다.")
                
            except Exception as e:
                st.error(f"제목 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 결과 출력 영역 - 하단에 배치
    if st.session_state.titles_generated or st.session_state.press_release:
        st.markdown("<h3 style='color:#2E4057; margin-top:30px; margin-bottom:20px;'>결과</h3>", unsafe_allow_html=True)
    
    # 제목 옵션 표시 영역
    if st.session_state.titles_generated and st.session_state.titles:
        with st.container():
            st.markdown("<h5 style='color:#4B7F9F; margin-bottom:-20px;'>제목 선택</h5>", unsafe_allow_html=True)
            
            selected_title = st.radio(
                "",
                st.session_state.titles,
                index=st.session_state.titles.index(st.session_state.selected_title) if st.session_state.selected_title in st.session_state.titles else 0,
                label_visibility="collapsed"
            )
            
            # 선택된 제목 저장
            st.session_state.selected_title = selected_title
            
            # 보도자료 생성 버튼
            if st.button("보도자료 생성하기", type="primary", use_container_width=True):
                with st.spinner("보도자료를 생성하고 있습니다..."):
                    try:
                        if model_provider == "OpenAI GPT-4o-mini":
                            st.session_state.press_release = generate_press_release_with_openai(
                                st.session_state.selected_title,
                                st.session_state.core_content,
                                st.session_state.keywords,
                                temperature,
                                st.session_state.style_option
                            )
                        else:  # Google Gemini
                            st.session_state.press_release = generate_press_release_with_gemini(
                                st.session_state.selected_title,
                                st.session_state.core_content,
                                st.session_state.keywords,
                                temperature,
                                st.session_state.style_option
                            )
                        st.success("보도자료가 생성되었습니다.")
                    except Exception as e:
                        st.error(f"보도자료 생성 중 오류가 발생했습니다: {str(e)}")

    # 보도자료 표시 영역
    if st.session_state.press_release:
        with st.container():
            st.markdown("<h5 style='color:#4B7F9F; margin-top:20px; margin-bottom:-20px;'>생성된 보도자료</h5>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="press-release">
                <div class="press-title">{st.session_state.selected_title}</div>
                <div class="press-content">
                    {st.session_state.press_release}
            """, unsafe_allow_html=True)
            
            # 버튼 행 (복사 및 새로 만들기)
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("텍스트 복사", type="secondary", use_container_width=True):
                    st.markdown(f"""
                    <script>
                    navigator.clipboard.writeText(`{st.session_state.selected_title}\n\n{st.session_state.press_release.replace("`", "\\`")}`);
                    </script>
                    """, unsafe_allow_html=True)
                    st.success("클립보드에 복사되었습니다!")
            
            with btn_col2:
                if st.button("새 보도자료 작성", use_container_width=True):
                    st.session_state.core_content = ""
                    st.session_state.keywords = ["", "", "", "", "", ""]
                    st.session_state.titles = []
                    st.session_state.selected_title = ""
                    st.session_state.press_release = ""
                    st.session_state.titles_generated = False
                    st.session_state.style_option = "standard"
                    st.rerun()