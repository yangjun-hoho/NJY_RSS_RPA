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
        st.caption("© 2025 남양주시 AI 인사말씀 생성기")

    # 메인 영역 스타일 적용
    st.markdown("""
    <style>
    .greeting-content {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    .greeting-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    .greeting-text {
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
    /* 선택 옵션 스타일 */
    .stRadio label, .stSelectbox label {
        font-size: 14px !important;
    }
    /* 선택 컨테이너 스타일 */
    .option-container {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if "core_content" not in st.session_state:
        st.session_state.core_content = ""
    if "greeting_generated" not in st.session_state:
        st.session_state.greeting_generated = False
    if "greeting_text" not in st.session_state:
        st.session_state.greeting_text = ""
    
    # 인사말 옵션 데이터
    speaker_options = ["시장", "부시장", "국장", "과장", "팀장", "주무관"]
    greeting_type_options = ["환영사", "축사", "기념사", "개회사", "폐회사", "시무식", "종무식", "시상식"]
    audience_type1_options = ["시민", "공무원", "기업인", "학생", "어르신", "외국인", "관광객", "주민"]
    audience_type2_options = ["일반", "전문가", "귀빈", "참가자", "수상자", "자원봉사자", "내빈"]
    
    quote_type1_options = ["없음", "명언", "격언", "시", "노래가사", "속담", "고사성어"]
    quote_type2_options = ["없음", "영감을 주는", "위로하는", "도전적인", "감사의", "축하의", "격려의"]
    season_options = ["봄", "여름", "가을", "겨울", "신년", "연말", "특정 명절이나 기념일 없음"]
    situation_options = ["일반적 상황", "경기침체", "여론악화", "재난피해", "재난복구", "국가적 경사", "지역 발전"]

    # OpenAI GPT API 호출 함수 - 인사말 생성
    def generate_greeting_with_openai(options, temperature):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        연설자: {options['speaker']}
        인사말 성격: {options['greeting_type']}
        주요 청중1: {options['audience_type1']}
        주요 청중2: {options['audience_type2']}
        인용구 유형: {options['quote_type1']}
        인용구 성격: {options['quote_type2']}
        계절/시기: {options['season']}
        현재 상황: {options['situation']}
        추가 내용: {options['core_content']}
        
        위 정보를 바탕으로 정중하고 격식 있는 인사말씀을 작성해주세요.
        인사말은 시작 인사, 본문, 마무리 인사로 구성해주세요.
        총 700-800자 정도로 작성해주세요.
        
        만약 인용구 유형이 '없음'이 아니라면, 적절한 인용구를 포함해주세요.
        인용구 성격이 '없음'이 아니라면, 해당 성격에 맞는 인용구를 선택해주세요.
        계절/시기와 현재 상황을 자연스럽게 언급해주세요.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        return response.choices[0].message.content

    # Gemini API 호출 함수 - 인사말 생성
    def generate_greeting_with_gemini(options, temperature):
        genai.configure(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        너는 다른 AI보다 인사말씀 등 글쓰기 능력이 뛰어나다고 들었어 
        연설자: {options['speaker']}
        인사말 성격: {options['greeting_type']}
        주요 청중1: {options['audience_type1']}
        주요 청중2: {options['audience_type2']}
        인용구 유형: {options['quote_type1']}
        인용구 성격: {options['quote_type2']}
        계절/시기: {options['season']}
        현재 상황: {options['situation']}
        추가 내용: {options['core_content']}
        
        위 정보를 바탕으로 정중하고 격식 있는 인사말씀을 작성하고
        인사말은 시작 인사, 본문, 마무리 인사로 구성해줘
        총 700-800자 정도로 작성해줘
        
        만약 인용구 유형이 '없음'이 아니라면, 적절한 인용구를 포함해주고
        인용구 성격이 '없음'이 아니라면, 해당 성격에 맞는 인용구를 선택해줘
        계절/시기와 현재 상황을 자연스럽게 언급해주고 
        서두르지 말고 깊이 생각하고 최고의 인사말씀씀을 작성해줘 
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                    generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        return response.text

    # 메인 레이아웃
    st.title("👋 AI 인사말씀 생성기")
    st.caption("필요한 옵션을 선택하고, AI가 맞춤형 인사말씀을 생성해드립니다.")
    
    # 입력 폼 영역
    with st.form(key="greeting_form"):
        st.markdown("<h3 style='color:#2E4057; margin-bottom:15px;'>인사말씀 옵션 선택</h3>", unsafe_allow_html=True)
        
        # 첫번째 행: 연설자, 인사말 성격, 청중선택1, 청중선택2

        row1_cols = st.columns(4)
        
        with row1_cols[0]:
            speaker = st.selectbox("연설자 선택", speaker_options, 
                                 help="인사말씀을 전달할 사람의 직위를 선택하세요")
        
        with row1_cols[1]:
            greeting_type = st.selectbox("인사말 성격", greeting_type_options,
                                     help="어떤 성격의 인사말씀이 필요한지 선택하세요")
        
        with row1_cols[2]:
            audience_type1 = st.selectbox("청중 선택 1", audience_type1_options,
                                      help="주요 청중층을 선택하세요")
        
        with row1_cols[3]:
            audience_type2 = st.selectbox("청중 선택 2", audience_type2_options,
                                      help="추가 청중층을 선택하세요")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 두번째 행: 인용구선택1, 인용구선택2, 계절선택, 현황상황
        #st.markdown("<div class='option-container'>", unsafe_allow_html=True)
        row2_cols = st.columns(4)
        
        with row2_cols[0]:
            quote_type1 = st.selectbox("인용구 유형", quote_type1_options,
                                    help="인사말에 포함할 인용구의 유형을 선택하세요")
        
        with row2_cols[1]:
            quote_type2 = st.selectbox("인용구 성격", quote_type2_options,
                                    help="인용구의 성격을 선택하세요")
        
        with row2_cols[2]:
            season = st.selectbox("계절/시기 선택", season_options,
                                help="인사말의 시기적 배경을 선택하세요")
        
        with row2_cols[3]:
            situation = st.selectbox("현재 상황", situation_options,
                                  help="현재의 사회적/경제적 상황을 선택하세요")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 추가 내용 입력
        st.markdown("<h5 style='color:#4B7F9F; margin-top:10px; margin-bottom:10px;'>추가 내용</h5>", unsafe_allow_html=True)
        core_content = st.text_area("",
                             value=st.session_state.core_content,
                             height=150,
                             placeholder="인사말씀에 꼭 포함되어야 할 내용이 있다면 입력하세요.")
        
        # 생성 버튼
        generate_button = st.form_submit_button(
            label="인사말씀 생성하기",
            use_container_width=True,
            type="primary"
        )
    
    # 폼 제출 처리
    if generate_button:
        # 입력 내용 저장
        st.session_state.core_content = core_content
        
        # 옵션 정보 수집
        greeting_options = {
            'speaker': speaker,
            'greeting_type': greeting_type,
            'audience_type1': audience_type1,
            'audience_type2': audience_type2,
            'quote_type1': quote_type1,
            'quote_type2': quote_type2,
            'season': season,
            'situation': situation,
            'core_content': core_content
        }
        
        # 인사말 생성 로직 실행
        with st.spinner("맞춤형 인사말씀을 생성하고 있습니다..."):
            try:
                if model_provider == "OpenAI GPT-4o":
                    st.session_state.greeting_text = generate_greeting_with_openai(
                        greeting_options,
                        temperature
                    )
                else:  # Google Gemini
                    st.session_state.greeting_text = generate_greeting_with_gemini(
                        greeting_options,
                        temperature
                    )
                
                st.session_state.greeting_generated = True
                st.success("인사말씀이 생성되었습니다.")
                
            except Exception as e:
                st.error(f"인사말씀 생성 중 오류가 발생했습니다: {str(e)}")

    # 생성된 인사말씀 표시 영역
    if st.session_state.greeting_generated and st.session_state.greeting_text:
        st.markdown("<h3 style='color:#2E4057; margin-top:20px; margin-bottom:15px;'>생성된 인사말씀</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="greeting-content">
            <div class="greeting-title">{greeting_type} - {speaker}</div>
            <div class="greeting-text">
                {st.session_state.greeting_text}

        """, unsafe_allow_html=True)
        
        # 버튼 행 (복사 및 새로 만들기)
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("텍스트 복사", type="secondary", use_container_width=True):
                st.markdown(f"""
                <script>
                navigator.clipboard.writeText(`{st.session_state.greeting_text.replace("`", "\\`")}`);
                </script>
                """, unsafe_allow_html=True)
                st.success("클립보드에 복사되었습니다!")
        
        with btn_col2:
            if st.button("새 인사말씀 작성", use_container_width=True):
                st.session_state.core_content = ""
                st.session_state.greeting_text = ""
                st.session_state.greeting_generated = False
                st.rerun()