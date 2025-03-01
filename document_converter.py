import streamlit as st
import openai
from openai import OpenAI
import google.generativeai as genai
import os
import tempfile
import PyPDF2
from dotenv import load_dotenv

def run():
    # API 키 로드
    load_dotenv()
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
        st.caption("© 2025 남양주시 AI문서자료 대본 생성기")

    # 메인 영역 스타일 적용
    st.markdown("""
    <style>
    .content-output {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        max-height: 600px;
        overflow-y: auto;
    }
    .output-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    .output-text {
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
    /* 텍스트 영역 상단 여백 조정 */
    .stTextArea {
        margin-top: 0rem !important;
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
    if "doc_converter_content" not in st.session_state:
        st.session_state.doc_converter_content = ""
    if "doc_converter_output_generated" not in st.session_state:
        st.session_state.doc_converter_output_generated = False
    if "doc_converter_output_text" not in st.session_state:
        st.session_state.doc_converter_output_text = ""
    
    # 출력 유형 옵션
    output_type_options = ["발표대본", "시나리오", "회의진행문", "브리핑자료", "요약본"]
    
    # 역할 및 상황 옵션
    role_options = ["공무원", "팀장", "사업 담당자", "교육 강사", "진행자", "사회자", "기타"]
    audience_options = ["시민", "공무원", "기업인", "학생", "어르신", "외국인", "관광객", "주민", "참석자"]
    situation_options = ["일반적 상황", "공식 행사", "내부 회의", "시민 설명회", "기자회견", "교육 세미나", "토론회", "기타"]
    
    # PDF 텍스트 추출 함수
    def extract_text_from_pdf(pdf_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.read())
            temp_path = temp_file.name
        
        text = ""
        try:
            with open(temp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
        except Exception as e:
            st.error(f"PDF 파일 읽기 오류: {str(e)}")
        finally:
            os.unlink(temp_path)
        
        return text

    # OpenAI API 호출 함수
    def generate_content_with_openai(options, document_text, temperature):
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        문서 내용: 
        {document_text}
        
        변환 유형: {options['output_type']}
        역할: {options['role']}
        청중: {options['audience']}
        상황: {options['situation']}
        
        위 문서 내용을 바탕으로 {options['output_type']}을(를) 작성해주세요.
        역할은 {options['role']}이고, 청중은 {options['audience']}입니다.
        상황은 {options['situation']}입니다.
        
        다음 지침을 따라주세요:
        1. 문서의 핵심 내용을 모두 포함하되, 자연스러운 말투로 변환해주세요.
        2. 발표대본인 경우, 시작 인사, 본문, 마무리 인사 구조로 작성해주세요.
        3. 시나리오인 경우, 상황 설명과 대화를 포함해주세요.
        4. 회의진행문인 경우, 진행 순서와 말씀을 포함해주세요.
        5. 브리핑자료인 경우, 간결하고 명확한 설명 포인트를 작성해주세요.
        6. 요약본인 경우, 핵심 내용만 간결하게 요약해주세요.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        return response.choices[0].message.content

    # Gemini API 호출 함수
    def generate_content_with_gemini(options, document_text, temperature):
        genai.configure(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        문서 내용: 
        {document_text}
        
        변환 유형: {options['output_type']}
        역할: {options['role']}
        청중: {options['audience']}
        상황: {options['situation']}
        
        위 문서 내용을 바탕으로 {options['output_type']}을(를) 작성해주세요.
        역할은 {options['role']}이고, 청중은 {options['audience']}입니다.
        상황은 {options['situation']}입니다.
        
        다음 지침을 따라주세요:
        1. 문서의 핵심 내용을 모두 포함하되, 자연스러운 말투로 변환해주세요.
        2. 발표대본인 경우, 시작 인사, 본문, 마무리 인사 구조로 작성해주세요.
        3. 시나리오인 경우, 상황 설명과 대화를 포함해주세요.
        4. 회의진행문인 경우, 진행 순서와 말씀을 포함해주세요.
        5. 브리핑자료인 경우, 간결하고 명확한 설명 포인트를 작성해주세요.
        6. 요약본인 경우, 핵심 내용만 간결하게 요약해주세요.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                     generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        return response.text

    # 메인 레이아웃
    st.title("📝 AI문서자료 대본 생성기")
    st.caption("PDF 문서(공고/안내/계획/보고 등)를 업로드하여 발표대본, 시나리오, 회의진행문 등으로 변환해보세요.")
    
    # 문서 입력 영역
    st.subheader("문서 업로드 또는 텍스트 입력")
    
    # 파일 업로드 또는 텍스트 입력 선택
    input_method = st.radio("입력 방식 선택", ["PDF 파일 업로드", "직접 텍스트 입력"])
    
    if input_method == "PDF 파일 업로드":
        uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])
        if uploaded_file is not None:
            with st.spinner("PDF 내용을 추출하는 중..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
                if extracted_text:
                    st.session_state.doc_converter_content = extracted_text
                    st.success("PDF 내용이 추출되었습니다.")
                    st.text_area("추출된 텍스트", value=st.session_state.doc_converter_content, height=250)
    else:
        st.session_state.doc_converter_content = st.text_area(
            "문서 내용을 입력하세요",
            value=st.session_state.doc_converter_content,
            height=350,
            placeholder="여기에 변환하고 싶은 문서의 내용을 입력하세요."
        )
    
    # 상황 옵션 영역
    if st.session_state.doc_converter_content:
        st.subheader("상황 옵션 설정")
        
        # 모든 옵션을 한 행에 배치
        st.markdown("<div class='option-container'>", unsafe_allow_html=True)
        row_cols = st.columns(4)
        
        with row_cols[0]:
            situation = st.selectbox("상황 선택", situation_options,
                                  help="어떤 상황에서 사용할지 선택하세요")
        
        with row_cols[1]:
            output_type = st.selectbox("변환 유형", output_type_options, 
                                     help="문서를 어떤 형태로 변환할지 선택하세요")
        
        with row_cols[2]:
            role = st.selectbox("역할 선택", role_options,
                              help="어떤 역할로 말하는지 선택하세요")
        
        with row_cols[3]:
            audience = st.selectbox("청중 선택", audience_options,
                                  help="주요 청중을 선택하세요")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 변환 버튼
        generate_button = st.button(
            label="변환하기",
            type="primary",
            use_container_width=True
        )
        
        # 변환 버튼 클릭 처리
        if generate_button:
            # 옵션 정보 수집
            conversion_options = {
                'output_type': output_type,
                'role': role,
                'audience': audience,
                'situation': situation
            }
            
            # 변환 로직 실행
            with st.spinner(f"{output_type}으로 변환 중입니다..."):
                try:
                    if model_provider == "OpenAI GPT-4o":
                        st.session_state.doc_converter_output_text = generate_content_with_openai(
                            conversion_options,
                            st.session_state.doc_converter_content,
                            temperature
                        )
                    else:  # Google Gemini
                        st.session_state.doc_converter_output_text = generate_content_with_gemini(
                            conversion_options,
                            st.session_state.doc_converter_content,
                            temperature
                        )
                    
                    st.session_state.doc_converter_output_generated = True
                    st.success("변환이 완료되었습니다.")
                    
                except Exception as e:
                    st.error(f"변환 중 오류가 발생했습니다: {str(e)}")

    # 변환 결과 표시 영역
    if st.session_state.doc_converter_output_generated and st.session_state.doc_converter_output_text:
        st.markdown("<h3 style='color:#2E4057; margin-top:20px; margin-bottom:15px;'>변환 결과</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="content-output">
            <div class="output-title">{output_type}</div>
            <div class="output-text">
                {st.session_state.doc_converter_output_text.replace("`", "\\`").replace("\n", "<br>")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 버튼 행 (복사 및 새로 작성)
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("텍스트 복사", type="secondary", use_container_width=True):
                st.markdown(f"""
                <script>
                navigator.clipboard.writeText(`{st.session_state.doc_converter_output_text.replace("`", "\\`")}`);
                </script>
                """, unsafe_allow_html=True)
                st.success("클립보드에 복사되었습니다!")
        
        with btn_col2:
            if st.button("새 변환 작성", use_container_width=True):
                st.session_state.doc_converter_output_text = ""
                st.session_state.doc_converter_output_generated = False
                st.rerun()