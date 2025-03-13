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
    
    # 인사말 옵션 데이터 - 수정된 부분
    situation_options = ["없음", "월례조회", "보고회", "간담회", "일반회의", "행사", "축제", "강연", "모임"]
    greeting_type_options = ["개회사", "환영사", "축사", "기념사", "폐회사", "시무식", "종무식", "시상식"]
    speaker_options = ["시장", "부시장", "국장", "과장"]
    audience_type1_options = ["시민", "공무원", "기업인", "학생", "어르신", "외국인", "관광객", "주민"]
    audience_type2_options = ["없음", "일반", "전문가", "귀빈", "참가자", "수상자", "자원봉사자", "내빈"]
    
    quote_type1_options = ["없음","정약용선생 말씀", "명언", "격언", "고사성어", "속담", "시", "노래가사"]
    quote_type2_options = ["없음", "도전적인", "감사의", "축하의", "격려의", "영감을 주는", "위로하는"]
    season_options = ["없음", "봄", "여름", "가을", "겨울", "신년", "연말", "특정 명절이나 기념일 없음"]
    namyangju_situation_options = ["일반적 상황", "경기침체", "여론악화", "재난피해", "재난복구", "지역 발전", "축제 개최"]
    speech_style_options = ["격식 있는", "친근한", "간결한", "감성적인", "설득력 있는", "권위적인", "유머러스한"]

    # OpenAI GPT API 호출 함수 - 인사말 생성
    def generate_greeting_with_openai(options, temperature):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        당신은 대한민국의 명문 연설문 작가로, 30년 경력을 가진 최고의 전문가입니다. 정치인, 기업인, 공무원의 연설을 작성해왔고, 특히 공적 자리의 인사말씀에 정통합니다.

        # 연설 정보
        상황: {options['situation']}
        인사말 성격: {options['greeting_type']}
        연설자: {options['speaker']}
        주요 청중1: {options['audience_type1']}
        주요 청중2: {options['audience_type2']}
        인용구 유형: {options['quote_type1']}
        인용구 성격: {options['quote_type2']}
        계절/시기: {options['season']}
        남양주시 상황: {options['namyangju_situation']}
        연설 스타일: {options['speech_style']}
        추가 내용: {options['core_content']}

        # 작성 지침
        1. 인사말은 '도입부-본문-결어'의 3단 구조로 작성하되, 자연스러운 흐름을 유지하십시오.
        2. 도입부(20%): 
        - 청중에 대한 존중과 감사로 시작
        - 현 상황 및 계절감을 반영한 시의성 있는 표현
        - 청중의 특성에 맞는 공감대 형성

        3. 본문(60%):
        - 핵심 메시지를 3가지 이내로 명확하게 전달
        - {options['quote_type1']} 유형의 인용구를 적절히 활용하여 메시지 강화
        - 인용구는 {options['quote_type2']} 성격을 띄도록 선정
        - 남양주시 현안({options['namyangju_situation']}과 {options['core_content']})을 자연스럽게 언급하되 과도한 정치적 색채는 배제
        - 구체적 사례나 숫자를 통해 설득력 강화

        4. 결어(20%):
        - 희망적 메시지로 마무리
        - 청중에게 구체적인 행동 제안이나 기대 표현
        - 감사와 존중의 재표현

        # 문체 지침
        - {options['speech_style']} 스타일을 일관되게 유지
        - 간결하고 명확한 문장 사용 (문장당 45자 이내)
        - 화려한 수식어보다 강한 동사 사용 권장
        - 청자를 존중하는 어휘 선택 (높임말 적절히 사용)
        - 전문용어는 꼭 필요한 경우에만 사용하고 설명 병기
        - 비유와 은유를 통해 생동감 있는 표현 구사
        - 글자 수: 1000~1200자 내외로 작성

        이 인사말씀은 문서로 기록되고, 청중에게 직접 낭독될 것임을 명심하십시오. 음성으로 전달될 때 자연스러운 호흡과 강조가 가능하도록 작성하세요.

        # 최종 검토 사항
        - 정서적 공감대 형성이 되었는가?
        - 핵심 메시지가 명확한가?
        - 시의적절한 내용인가?
        - 인용구가 적절히 활용되었는가?
        - 지역 특성이 반영되었는가?
        - 요청된 스타일에 부합하는가?

        최고의 연설문 작가로서의 역량을 모두 발휘하여 작성해 주십시오.
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
        당신은 대한민국의 명문 연설문 작가로, 30년 경력을 가진 최고의 전문가입니다. 정치인, 기업인, 공무원의 연설을 작성해왔고, 특히 공적 자리의 인사말씀에 정통합니다.

        # 연설 정보
        상황: {options['situation']}
        인사말 성격: {options['greeting_type']}
        연설자: {options['speaker']}
        주요 청중1: {options['audience_type1']}
        주요 청중2: {options['audience_type2']}
        인용구 유형: {options['quote_type1']}
        인용구 성격: {options['quote_type2']}
        계절/시기: {options['season']}
        남양주시 상황: {options['namyangju_situation']}
        연설 스타일: {options['speech_style']}
        추가 내용: {options['core_content']}

        # 작성 지침
        1. 인사말은 '도입부-본문-결어'의 3단 구조로 작성하되, 자연스러운 흐름을 유지하십시오.
        2. 도입부(20%): 
        - 청중에 대한 존중과 감사로 시작
        - 현 상황 및 계절감을 반영한 시의성 있는 표현
        - 청중의 특성에 맞는 공감대 형성

        3. 본문(60%):
        - 핵심 메시지를 3가지 이내로 명확하게 전달
        - {options['quote_type1']} 유형의 인용구를 적절히 활용하여 메시지 강화
        - 인용구는 {options['quote_type2']} 성격을 띄도록 선정
        - 남양주시 현안({options['namyangju_situation']}과 {options['core_content']})을 자연스럽게 언급하되 과도한 정치적 색채는 배제
        - 구체적 사례나 숫자를 통해 설득력 강화

        4. 결어(20%):
        - 희망적 메시지로 마무리
        - 청중에게 구체적인 행동 제안이나 기대 표현
        - 감사와 존중의 재표현

        # 문체 지침
        - {options['speech_style']} 스타일을 일관되게 유지
        - 간결하고 명확한 문장 사용 (문장당 45자 이내)
        - 화려한 수식어보다 강한 동사 사용 권장
        - 청자를 존중하는 어휘 선택 (높임말 적절히 사용)
        - 전문용어는 꼭 필요한 경우에만 사용하고 설명 병기
        - 비유와 은유를 통해 생동감 있는 표현 구사
        - 글자 수: 1000~1200자 내외로 작성

        이 인사말씀은 문서로 기록되고, 청중에게 직접 낭독될 것임을 명심하십시오. 음성으로 전달될 때 자연스러운 호흡과 강조가 가능하도록 작성하세요.

        # 최종 검토 사항
        - 정서적 공감대 형성이 되었는가?
        - 핵심 메시지가 명확한가?
        - 시의적절한 내용인가?
        - 인용구가 적절히 활용되었는가?
        - 지역 특성이 반영되었는가?
        - 요청된 스타일에 부합하는가?

        최고의 연설문 작가로서의 역량을 모두 발휘하여 작성해 주십시오.
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
        
        # 첫번째 행: 상황, 인사말 성격, 연설자, 청중선택1, 청중선택2
        row1_cols = st.columns(5)
        
        with row1_cols[0]:
            situation = st.selectbox("상황 선택", situation_options, 
                                 help="인사말씀이 필요한 상황을 선택하세요")
        
        with row1_cols[1]:
            greeting_type = st.selectbox("인사말 성격", greeting_type_options,
                                     help="어떤 성격의 인사말씀이 필요한지 선택하세요")
        
        with row1_cols[2]:
            speaker = st.selectbox("연설자 선택", speaker_options, 
                                help="인사말씀을 전달할 사람의 직위를 선택하세요")
        
        with row1_cols[3]:
            audience_type1 = st.selectbox("청중 선택 1", audience_type1_options,
                                      help="주요 청중층을 선택하세요")
        
        with row1_cols[4]:
            audience_type2 = st.selectbox("청중 선택 2", audience_type2_options,
                                      help="추가 청중층을 선택하세요")
        
        # 두번째 행: 인용구 유형, 인용구 성격, 계절/시기, 남양주시 상황, 연설 스타일
        row2_cols = st.columns(5)
        
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
            namyangju_situation = st.selectbox("남양주시 상황", namyangju_situation_options,
                                  help="현재 남양주시의 상황을 선택하세요")
        
        with row2_cols[4]:
            speech_style = st.selectbox("연설 스타일", speech_style_options,
                                    help="인사말씀의 전달 스타일을 선택하세요")
        
        # 추가 내용 입력
        st.markdown("<h5 style='color:#4B7F9F; margin-top:10px; margin-bottom:10px;'>추가 내용</h5>", unsafe_allow_html=True)
        core_content = st.text_area("",
                             value=st.session_state.core_content,
                             height=150,
                             placeholder="축제, 행사, 보고회의 구체적 명칭, 인사말씀 중에 꼭 포함되어야 할 전달사항이나 특이사항 있다면 입력하세요.")
        
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
        
        # 옵션 정보 수집 - 수정된 부분
        greeting_options = {
            'situation': situation,
            'greeting_type': greeting_type,
            'speaker': speaker,
            'audience_type1': audience_type1,
            'audience_type2': audience_type2,
            'quote_type1': quote_type1,
            'quote_type2': quote_type2,
            'season': season,
            'namyangju_situation': namyangju_situation,
            'speech_style': speech_style,
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