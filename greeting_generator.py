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
        st.title("📜 AI 인사말씀 생성기")
        
        # AI 모델 선택
        model_provider = st.radio(
            "□ AI모델 선택",
            ["OpenAI GPT", "Google Gemini"]
        )
        
        # 공통 설정
        temperature = st.slider("□ 창의성 수준", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        greeting_length = st.select_slider(
            "인사말 길이",
            options=["짧게 (1-2분)", "중간 (3-5분)", "길게 (5-7분)"]
        )
        
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
    .option-group {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
    }
    .option-label {
        font-weight: bold;
        margin-bottom: 5px;
        color: #2c3e50;
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
    /* 스트림릿 컨테이너 간격 조정 */
    .element-container {
        margin-top: 0.05rem !important;
        margin-bottom: 0.1rem !important;
    }
    /* 마크다운 간격 조정 */
    p {
        margin-bottom: 0.1rem !important;
    }
    /* 옵션 라벨 아래 간격 줄이기 */
    .option-label + div {
        margin-top: -2px;
    }
    /* 텍스트 영역 아래 간격 줄이기 */
    .stTextArea {
        margin-bottom: 0.5rem !important;
    }
    /* 제목 간격 줄이기 */
    .markdown-text-container {
        margin-bottom: 0.2rem !important;
    }            
    </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if "greeting_core_content" not in st.session_state:
        st.session_state.greeting_core_content = ""
    if "greeting_result" not in st.session_state:
        st.session_state.greeting_result = ""
    if "greeting_options" not in st.session_state:
        st.session_state.greeting_options = {
            "greeting_type": "대중적",
            "speaker": "남양주시장",
            "audience1": "시민",
            "audience2": "없음",
            "season": "없음",
            "quote": "없음",
            "disaster": "없음"
        }

    # OpenAI GPT API 호출 함수 - 인사말씀 생성
    def generate_greeting_with_openai(core_content, options, temperature, length):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 길이별 단어 수 설정
        length_guide = {
            "짧게 (1-2분)": "300-500자",
            "중간 (3-5분)": "700-1000자",
            "길게 (5-7분)": "1200-1500자"
        }
        
        prompt = f"""
        인사말씀 작성을 위한 정보:
        
        기본 내용: {core_content}
        
        인사말 성격: {options['greeting_type']}
        연설자: {options['speaker']}
        주요 청중: {options['audience1']}
        부가 청중: {options['audience2']}
        계절 관련: {options['season']}
        인용구 스타일: {options['quote']}
        재난 상황 언급: {options['disaster']}
        
        위 정보를 바탕으로 공식적이고 적절한 인사말씀을 작성해주세요.
        청중과 상황에 맞게 존칭과 예의를 갖춘 말투를 사용하세요.
        인사말은 {length_guide[length]} 정도의 길이로 작성해주세요.
        
        인사말의 구성:
        1. 인사와 소개
        2. 행사/상황에 대한 언급
        3. 주요 메시지 전달
        4. 청중에 대한 감사와 마무리
        
        특별 요청:
        - {options['greeting_type']}에 맞는 적절한 톤과 어휘를 사용하세요
        - {options['speaker']} 직위에 적합한 말투와 어휘를 사용하세요
        - {options['audience1']}을(를) 주 대상으로 하는 내용을 포함하세요
        - {options['audience2']}가 '없음'이 아니라면 해당 대상을 고려한 내용도 추가하세요
        - {options['season']}이 '없음'이 아니라면 해당 계절에 관련된 표현을 적절히 사용하세요
        - {options['quote']}가 '없음'이 아니라면 해당 스타일의 인용구나 표현을 1-2개 포함시키세요
        - {options['disaster']}가 '없음'이 아니라면 해당 재난 상황에 대한 위로와 격려의 메시지를 포함하세요
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        return response.choices[0].message.content

    # Gemini API 호출 함수 - 인사말씀 생성
    def generate_greeting_with_gemini(core_content, options, temperature, length):
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 길이별 단어 수 설정
        length_guide = {
            "짧게 (1-2분)": "300-500자",
            "중간 (3-5분)": "700-1000자",
            "길게 (5-7분)": "1200-1500자"
        }
        
        prompt = f"""
        인사말씀 작성을 위한 정보:
        
        기본 내용: {core_content}
        
        인사말 성격: {options['greeting_type']}
        연설자: {options['speaker']}
        주요 청중: {options['audience1']}
        부가 청중: {options['audience2']}
        계절 관련: {options['season']}
        인용구 스타일: {options['quote']}
        재난 상황 언급: {options['disaster']}
        
        위 정보를 바탕으로 공식적이고 적절한 인사말씀을 작성해주세요.
        청중과 상황에 맞게 존칭과 예의를 갖춘 말투를 사용하세요.
        인사말은 {length_guide[length]} 정도의 길이로 작성해주세요.
        
        인사말의 구성:
        1. 인사와 소개
        2. 행사/상황에 대한 언급
        3. 주요 메시지 전달
        4. 청중에 대한 감사와 마무리
        
        특별 요청:
        - {options['greeting_type']}에 맞는 적절한 톤과 어휘를 사용하세요
        - {options['speaker']} 직위에 적합한 말투와 어휘를 사용하세요
        - {options['audience1']}을(를) 주 대상으로 하는 내용을 포함하세요
        - {options['audience2']}가 '없음'이 아니라면 해당 대상을 고려한 내용도 추가하세요
        - {options['season']}이 '없음'이 아니라면 해당 계절에 관련된 표현을 적절히 사용하세요
        - {options['quote']}가 '없음'이 아니라면 해당 스타일의 인용구나 표현을 1-2개 포함시키세요
        - {options['disaster']}가 '없음'이 아니라면 해당 재난 상황에 대한 위로와 격려의 메시지를 포함하세요
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                    generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        return response.text

    # 메인 레이아웃
    st.title("AI 인사말씀 생성기")
    st.caption("주요 내용을 입력하고 옵션을 선택하면, AI가 상황에 맞는 인사말씀을 생성해드립니다.")

    # 상하 레이아웃으로 변경
    
    # 상단 영역 - 입력 영역
    st.subheader("< 입력 >")
    
    # form 생성
    with st.form(key="greeting_form"):
        # 핵심 내용 입력
        st.markdown("##### 인사말씀의 주요 내용")
        core_content = st.text_area("", 
                                value=st.session_state.greeting_core_content,
                                height=120,
                                placeholder="인사말씀에 포함할 주요 내용, 행사 정보, 특별 안내사항 등을 입력하세요")
        
        # 옵션 선택 영역
        st.markdown("##### 인사말씀 옵션 선택")
        
        # 리스트(드롭다운) 형식으로 옵션 선택 변경
        cols1 = st.columns(3)
        with cols1[0]:
            greeting_type = st.selectbox(
                "인사말 성격",
                ["대중적", "축제행사", "위원회", "명절"],
                index=["대중적", "축제행사", "위원회", "명절"].index(st.session_state.greeting_options["greeting_type"])
            )
        
        with cols1[1]:
            speaker = st.selectbox(
                "연설자 선택",
                ["남양주시장", "시의회 의장", "국장", "위원장"],
                index=["남양주시장", "시의회 의장", "국장", "위원장"].index(st.session_state.greeting_options["speaker"])
            )
            
        with cols1[2]:
            disaster = st.selectbox(
                "재난 상황",
                ["없음", "재난피해", "재난복구"],
                index=["없음", "재난피해", "재난복구"].index(st.session_state.greeting_options["disaster"])
            )
        
        cols2 = st.columns(3)
        with cols2[0]:
            audience1 = st.selectbox(
                "청중 선택1",
                ["시민", "학부모", "공직자", "개별위원"],
                index=["시민", "학부모", "공직자", "개별위원"].index(st.session_state.greeting_options["audience1"] if st.session_state.greeting_options["audience1"] not in ["oo시민", "관광객"] else "시민" if st.session_state.greeting_options["audience1"] == "oo시민" else "학부모")
            )
        
        with cols2[1]:
            audience2 = st.selectbox(
                "청중 선택2",
                ["없음", "청년", "학생", "장애인", "여성단체"],
                index=["없음", "청년", "학생", "장애인", "여성단체"].index(st.session_state.greeting_options["audience2"] if st.session_state.greeting_options["audience2"] in ["없음", "청년", "장애인", "여성단체"] else "없음")
            )
        
        with cols2[2]:
            season = st.selectbox(
                "계절 선택",
                ["없음", "봄", "여름", "가을", "겨울"],
                index=["없음", "봄", "여름", "가을", "겨울"].index(st.session_state.greeting_options["season"])
            )
        
        cols3 = st.columns([1, 2])
        with cols3[0]:
            quote = st.selectbox(
                "인용구 선택",
                ["없음", "감정이입", "한자성어", "속담", "영어격언"],
                index=["없음", "감정이입", "한자성어", "속담", "영어격언"].index(st.session_state.greeting_options["quote"])
            )
        
        # 폼 제출 버튼
        with cols3[1]:
            submit_button = st.form_submit_button(label="인사말씀 생성하기", type="primary", use_container_width=True)
        
        if submit_button:
            # 옵션 업데이트
            st.session_state.greeting_options.update({
                "greeting_type": greeting_type,
                "speaker": speaker,
                "audience1": audience1,
                "audience2": audience2,
                "season": season,
                "quote": quote,
                "disaster": disaster
            })
            
            # 핵심 내용 저장
            st.session_state.greeting_core_content = core_content
            
            # 인사말씀 생성
            with st.spinner("인사말씀을 생성하고 있습니다..."):
                try:
                    if model_provider == "OpenAI GPT":
                        st.session_state.greeting_result = generate_greeting_with_openai(
                            core_content,
                            st.session_state.greeting_options,
                            temperature,
                            greeting_length
                        )
                    else:  # Google Gemini
                        st.session_state.greeting_result = generate_greeting_with_gemini(
                            core_content,
                            st.session_state.greeting_options,
                            temperature,
                            greeting_length
                        )
                except Exception as e:
                    st.error(f"인사말씀 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 하단 영역 - 결과 출력 영역
    st.subheader("< 결과 >")
    
    # 인사말씀 표시 영역
    greeting_container = st.container()
    with greeting_container:
        if st.session_state.greeting_result:
            st.markdown("##### 생성된 인사말씀")
            
            # 메타데이터 표시
            meta_cols = st.columns(3)
            with meta_cols[0]:
                st.info(f"연설자: {st.session_state.greeting_options['speaker']}")
            with meta_cols[1]:
                st.info(f"주요 청중: {st.session_state.greeting_options['audience1']}")
            with meta_cols[2]:
                if st.session_state.greeting_options['audience2'] != "없음":
                    st.info(f"부가 청중: {st.session_state.greeting_options['audience2']}")
            
            st.markdown(f"""
            <div class="greeting-content">
                {st.session_state.greeting_result}
            </div>
            """, unsafe_allow_html=True)
            
            # 버튼 행 (복사 및 새로 만들기)
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("텍스트 복사", type="secondary"):
                    st.toast("클립보드에 복사되었습니다!")
            
            with btn_col2:
                if st.button("새 인사말씀 작성"):
                    st.session_state.greeting_core_content = ""
                    st.session_state.greeting_options = {
                        "greeting_type": "대중적",
                        "speaker": "남양주시장",
                        "audience1": "시민",
                        "audience2": "없음",
                        "season": "없음",
                        "quote": "없음",
                        "disaster": "없음"
                    }
                    st.session_state.greeting_result = ""
                    st.rerun()