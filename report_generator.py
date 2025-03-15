import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import openai
from openai import OpenAI
import google.generativeai as genai

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
        temperature = st.slider("⚙️ 창의성 수준", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
        
        st.divider()
        st.caption("© 2025 남양주시 AI보고서 생성기")
    
    # 페이지 스타일 설정
    st.markdown("""
    <style>
    h1 {
        font-size: 30px !important;
    }
    h3 {
        font-size: 16px !important;
        margin-top: 8px !important;
        margin-bottom: 4px !important;
    }
    .main-header {
        font-size: 2.5rem !important;
        font-weight: bold;
        margin-TOP: -3rem !important;    
        margin-bottom: -1rem !important;
    }
    .sub-header {
        font-size: 1rem !important;
        color: #666;
        margin-TOP: -1rem !important;         
        margin-bottom: 1rem !important;
    }
    .small-header {
        font-size: 1.3rem !important;
        margin-bottom: 0.8rem !important;
    }
    .section-header {
        font-size: 1rem !important;
        font-weight: bold;
        margin-bottom: 0.5rem !important;
    }
    /* 텍스트 영역 기본 높이 줄이기 */
    .stTextArea textarea {
        min-height: 50px !important;
    }
    /* 제목 폼 컴팩트하게 */
    div[data-baseweb="input"] {
        width: 100%;
    }
    /* 폼 간격 줄이기 */
    div.row-widget.stButton, div.row-widget.stDownloadButton {
        margin-top: 1rem !important;
    }  
    /* 모바일 화면에서 A4 용지 조정 */
    @media only screen and (max-width: 768px) {
        .a4-paper {
            width: 100%;
            padding: 1cm;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 앱 제목과 설명
    st.title("📝 AI 보고서 생성기")
    st.caption("보고서 유형과 서식을 선택하고 내용을 입력하면 AI가 보고서를 생성합니다.")
    
    # 상태 초기화
    if 'report_type' not in st.session_state:
        st.session_state.report_type = None
    if 'report_template' not in st.session_state:
        st.session_state.report_template = None
    if 'generated_report' not in st.session_state:
        st.session_state.generated_report = None
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # 1단계: 보고서 정보 선택
    st.markdown('<div class="small-header">1. 보고서 정보 선택</div>', unsafe_allow_html=True)
    
    # 보고서 유형과 서식 선택을 한 행에 배치
    col1, col2 = st.columns(2)
    
    # 보고서 유형 목록
    report_types = ["계획 보고서", "대책 보고서", "상황 보고서", "분석 보고서", "기타 보고서"]
    
    with col1:
        report_type = st.selectbox("보고서 유형", 
                                  options=report_types,
                                  index=None,
                                  placeholder="보고서 유형 선택...",
                                  key="report_type_select")
        
        if report_type:
            st.session_state.report_type = report_type
    
    # 2단계: 보고서 서식 선택 (보고서 유형이 선택된 경우에만)
    with col2:
        if st.session_state.report_type:
            templates = get_templates_for_type(st.session_state.report_type)
            template_names = list(templates.keys())
            
            template = st.selectbox("보고서 서식", 
                                   options=template_names,
                                   index=None,
                                   placeholder="서식 선택...",
                                   key="template_select")
            
            if template:
                st.session_state.report_template = template
                st.session_state.form_data = {field: "" for field in templates[template]}

    # 보고서 길이 제어만 유지 (스타일 옵션 제거)
    if st.session_state.report_template:
        col4 = st.columns(1)[0]
        
        with col4:
            length_options = [
                "표준 (기본 작성, 각 섹션당 2-3개의 문단)",
                "간략 (핵심 요약, 각 섹션당 1-2개의 문단)",
                "상세 (심층 분석, 각 섹션당 3-4개의 문단)"
            ]
            
            length_selected = st.selectbox(
                "보고서 길이",
                options=length_options,
                index=0,
                key="length_select"
            )
            
            if 'length' not in st.session_state:
                st.session_state.length = length_selected
            else:
                st.session_state.length = length_selected
    
    # 구분선 추가
    if st.session_state.report_template:
        st.markdown("---")
    
    # 3단계: 보고서 내용 입력 (서식이 선택된 경우에만)
    if st.session_state.report_template:
        try:
            st.markdown(f'<div class="small-header">2. 보고서 내용 입력</div>', unsafe_allow_html=True)
            st.caption("*제목만 입력해도 AI가 보고서를 생성하지만 입력내용이 풍부하면 더 잘 생성합니다.")
            st.markdown(f'<div class="section-header">{st.session_state.report_type} - {st.session_state.report_template}</div>', unsafe_allow_html=True)
            
            templates = get_templates_for_type(st.session_state.report_type)
            
            # 선택한 템플릿이 존재하는지 확인
            if st.session_state.report_template not in templates:
                st.error(f"선택한 서식 '{st.session_state.report_template}'를 찾을 수 없습니다. 다시 선택해주세요.")
                # 세션 상태 리셋
                st.session_state.report_template = None
                st.session_state.form_data = {}
                st.rerun()
            
            fields = templates[st.session_state.report_template]
            
            # 입력 폼 생성
            with st.form(key="report_form"):
                for i, field in enumerate(fields):
                    if field == "제목":
                        # 제목은 text_input으로 유지
                        st.session_state.form_data[field] = st.text_input(
                            f"{field}", 
                            value=st.session_state.form_data.get(field, ""),
                            key=f"input_{field}"
                        )
                    else:
                        # 다른 필드는 text_area로 변경하고 최소 높이 설정
                        st.session_state.form_data[field] = st.text_area(
                            f"{field}", 
                            value=st.session_state.form_data.get(field, ""),
                            key=f"input_{field}",
                            height=68  # 최소 높이 설정 (픽셀)
                        )
                
                submitted = st.form_submit_button("보고서 생성", use_container_width=True, type="primary")
                
                if submitted:
                    # 필수 필드 검증
                    if not st.session_state.form_data["제목"].strip():
                        st.error("제목은 필수 입력 항목입니다.")
                    else:
                        with st.spinner("AI가 보고서를 생성하고 있습니다... 잠시만 기다려주세요."):
                            report = generate_report(
                                model_provider,
                                temperature,
                                st.session_state.report_type,
                                st.session_state.report_template,
                                st.session_state.form_data,
                                st.session_state.length
                            )
                            st.session_state.generated_report = report
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.write("오류 세부정보:", e.__class__.__name__)
            import traceback
            st.code(traceback.format_exc())
    
    # 4단계: 생성된 보고서 표시
    if st.session_state.generated_report:
        st.markdown('<div class="small-header">3. 생성된 보고서</div>', unsafe_allow_html=True)
        
        # 보고서를 탭으로 표시
        report_tabs = st.tabs(["보고서 내용", "마크다운 코드"])
        
        with report_tabs[0]:
            # 보고서 스타일 적용
            st.markdown("""
            <style>
            .a4-container {
                display: flex;
                justify-content: center;
                width: 100%;
                margin: 20px 0;
            }
            .a4-paper {
                width: 21cm;
                min-height: 29.7cm;
                padding: 2cm;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                border: 1px solid #e0e0e0;
                overflow-wrap: break-word;
            }
            
            /* 보고서 내용 스타일 */
            .a4-paper h1 {
                font-size: 1.8rem !important;
                margin-top: -2rem !important;
                margin-bottom: 1rem !important;
                text-align: center !important;
            }
            
            .a4-paper h2 {
                font-size: 1.2rem !important;
                margin-top: 0.8rem !important;
                margin-bottom: 0.8rem !important;
                position: relative !important;
                padding-left: 1.5rem !important;
            }
            
            .a4-paper h2::before {
                content: "" !important;
                display: inline-block !important;
                width: 0.8rem !important;
                height: 0.8rem !important;
                background-color: black !important;
                position: absolute !important;
                left: 0 !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
            
            .a4-paper h3 {
                font-size: 1.1rem !important;
                margin-top: 0.6rem !important;
                margin-bottom: 0.6rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 보고서 내용 처리
            report_content = st.session_state.generated_report
            if "<style>" in report_content:
                content_part = report_content.split("</style>")[1]
            else:
                content_part = report_content
            
            # 전체 HTML 구성
            full_html = f"""
            <div class="a4-container">
                <div class="a4-paper">
                    {content_part}
            """
            
            # 렌더링
            st.markdown(full_html, unsafe_allow_html=True)
        
        with report_tabs[1]:
            # 마크다운 코드 표시
            markdown_code = st.session_state.generated_report
            if "<style>" in markdown_code:
                markdown_code = markdown_code.split("</style>")[1].strip()
            st.code(markdown_code, language="markdown")
        
        # 다운로드 옵션
        st.markdown('<div class="section-header">보고서 다운로드</div>', unsafe_allow_html=True)
        
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_title = st.session_state.form_data.get("제목", "보고서").replace(" ", "_")
        default_filename = f"{report_title}_{current_date}"
        
        filename = st.text_input("파일명", value=default_filename)
        
        # CSS 스타일 태그 제거
        markdown_content = st.session_state.generated_report
        if "<style>" in markdown_content:
            markdown_content = markdown_content.split("</style>")[1].strip()
        
        # 마크다운 다운로드 버튼
        st.download_button(
            label="마크다운 파일 다운로드",
            data=markdown_content,
            file_name=f"{filename}.md",
            mime="text/markdown",
            use_container_width=True
        )

def generate_report(model_provider, temperature, report_type, template_name, form_data, length):
    """선택된 모델에 따라 보고서 생성 함수 호출"""
    options = {
        "report_type": report_type,
        "template_name": template_name,
        "length": length
    }
    
    if model_provider == "OpenAI GPT-4o":
        report_content = generate_report_with_openai(options, form_data, temperature)
    else:  # Google Gemini
        report_content = generate_report_with_gemini(options, form_data, temperature)
    
    # 마크다운에 CSS를 추가하여 제목 크기 조정
    if report_content:
        markdown_with_css = f"""
<style>
h1 {{
    font-size: 1.5rem !important;
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
}}

h2 {{
    font-size: 1.2rem !important;
    margin-top: 0.8rem !important;
    margin-bottom: 0.8rem !important;
}}

h3 {{
    font-size: 1.1rem !important;
    margin-top: 0.6rem !important;
    margin-bottom: 0.6rem !important;
}}
</style>

{report_content}
"""
        return markdown_with_css
    
    return None

def get_templates_for_type(report_type):
    """보고서 유형에 따른 서식 목록을 반환"""
    templates = {
        "계획 보고서": {
            "기본 계획 서식": ["제목", "배경", "목적", "추진계획", "주요내용", "기대효과"],
            "세부 계획 서식": ["제목", "배경", "현황", "추진목표", "추진전략", "세부추진계획", "소요예산", "향후일정"],
            "사업계획 서식": ["제목", "사업개요", "추진배경", "사업내용", "추진일정", "소요예산", "기대효과"]
        },
        "대책 보고서": {
            "문제해결 서식": ["제목", "목적", "현황", "문제점", "대책", "효과"],
            "위기관리 서식": ["제목", "상황개요", "현안문제", "위험요소", "대응방안", "이행계획", "기대효과"],
            "개선안 서식": ["제목", "현상진단", "문제분석", "개선목표", "개선방안", "실행계획", "기대효과"]
        },
        "상황 보고서": {
            "현황 서식": ["제목", "보고일시", "상황개요", "현재상태", "조치사항", "향후계획"],
            "진행상황 서식": ["제목", "사업개요", "추진경과", "진행현황", "주요성과", "문제점", "향후계획"],
            "사건보고 서식": ["제목", "발생일시", "발생장소", "사건개요", "피해상황", "조치사항", "후속대책"]
        },
        "분석 보고서": {
            "데이터분석 서식": ["제목", "분석목적", "분석방법", "데이터개요", "분석결과", "시사점", "결론"],
            "성과분석 서식": ["제목", "사업개요", "분석목적", "성과지표", "분석결과", "개선사항", "결론"],
            "동향분석 서식": ["제목", "분석배경", "주요동향", "영향분석", "대응방안", "결론"]
        },
        "기타 보고서": {
            "간략메모 서식": ["제목", "날짜", "주요내용", "특이사항", "후속조치"],
            "회의결과 서식": ["제목", "회의일시", "참석자", "회의안건", "주요논의사항", "결정사항", "향후일정"],
            "업무메모 서식": ["제목", "작성일", "업무개요", "처리내용", "참고사항", "후속조치"]
        }
    }
    
    return templates.get(report_type, {})

def generate_report_with_openai(options, form_data, temperature):
    """OpenAI API를 사용하여 보고서 생성"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 현재 템플릿의 모든 필드 목록
    all_fields = list(form_data.keys())
    fields_structure = ", ".join(all_fields)
    
    # 프롬프트 구성
    fields_text = "\n".join([f"- {field}: {content}" for field, content in form_data.items() if content])
    
    # 길이 지침
    length_guidelines = {
        "표준 (기본 작성, 각 섹션당 2-3개의 문단)": "각 섹션당 2-3개의 문단으로 작성할 것. 균형 잡힌 내용과 적절한 상세 수준을 유지할 것.",
        "간략 (핵심 요약, 각 섹션당 1-2개의 문단)": "각 섹션당 1-2개의 간결한 문단으로 제한할 것. 핵심 요점만 포함하고 모든 불필요한 세부 사항은 제외할 것.",
        "상세 (심층 분석, 각 섹션당 3-4개의 문단)": "각 섹션을 3-5개의 문단으로 확장하여 깊이 있게 다룰 것. 배경 정보, 통계, 사례 연구 등 상세한 정보를 포함할 것."
    }
    
    selected_length_guideline = length_guidelines.get(options["length"], length_guidelines["표준 (기본 작성, 각 섹션당 2-3개의 문단)"])
    
    # 시스템 프롬프트 강화
    system_prompt = """당신은 전문적인 보고서를 작성하는 AI 조수입니다. 
반드시 개조식 문체로만 작성하세요.
서술형 문장(~합니다, ~됩니다, ~입니다 등)은 절대 사용하지 마세요.
개조식으로 작성된 보고서의 예시:
- 주민 편의 증진
- 예산 확보가 시급
- 추가 인력 배치 필요
- 사업의 성공적 추진을 위해 체계적인 접근이 중요"""
    
    prompt = f"""
당장 보고서 작성해! 너는 지자체 보고서 작성 전문가로 내가 시키는 대로 정확하게 작업할 거야.

## 서식 준수 - 절대 어기지 마!
내가 선택한 '{options["template_name"]}' 서식을 100% 그대로 따라야 해.
다음 순서대로 모든 섹션 하나도 빠짐없이 포함시켜: {fields_structure}

## 보고서 유형
{options["report_type"]}

## 보고서 서식
{options["template_name"]}

## 입력된 내용
{fields_text}

## 보고서 길이 요구사항
{selected_length_guideline}

## 작성 요구사항 - 반드시 준수!
1. 내가 입력한 정보는 그대로 활용하되, 부족한 부분은 네가 채워넣어.
2. 내가 제공한 서식 구조({fields_structure})는 절대 변경하지 마! 하나라도 빠지면 안 돼.
3. 입력 내용이 없는 섹션도 반드시 작성해서 완성된 보고서를 만들어.
4. 내가 내용을 거의 입력하지 않아도 네가 알아서 전문적인 내용으로 채워넣어야 해.
5. 공문서에 맞는 전문 용어와 공식적인 단어를를 사용해.
6. 마크다운으로 작성하되, 제목은 H1(#), 섹션은 H2(##)로 할 것.
7. 필요하면 표와 목록을 활용해서 정보를 명확하게 전달해.
8. 간결하고 명확한 문장으로 작성할 것.
9. 객관적이고 사실에 근거한 내용으로 채울 것.
10. 모든 내용을 개조식으로만 작성할 것. 배경이나 목표가 서설형인 경우우 마지막은 '~함', '~임', '~요함', '~필요함' 등으로 끝나야 함.
11. 절대로 서술형 문장(~합니다, ~됩니다, ~입니다 등)을 사용하지 말 것.

엄격하게 서식 구조를 따라야 해. 내가 제목만 주더라도 모든 섹션({fields_structure})을 빠짐없이 포함한 완벽한 보고서를 작성해! 네가 마음대로 섹션을 추가하거나 삭제하는 것은 용납 못 해.

마크다운 형식으로만 반환하고, 다른 설명이나 소개는 일절 포함하지 마!
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        
        # 서술형 문장이 있는지 확인하고, 있다면 개조식으로 변환 요청
        if '습니다' in result or '니다' in result:
            correction_prompt = f"""
다음 보고서를 완전한 개조식으로 다시 작성해주세요.
서술형('~합니다', '~됩니다', '~습니다' 등)은 절대 사용하지 마세요.

{result}
"""
            correction_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result = correction_response.choices[0].message.content
        
        return result
        
    except Exception as e:
        st.error(f"보고서 생성 중 오류가 발생했습니다: {str(e)}")
        if "api_key" in str(e).lower():
            st.error("OpenAI API 키가 올바르게 설정되어 있는지 확인하세요.")
        return None

def generate_report_with_gemini(options, form_data, temperature):
    """Gemini API를 사용하여 보고서 생성"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 현재 템플릿의 모든 필드 목록
    all_fields = list(form_data.keys())
    fields_structure = ", ".join(all_fields)
    
    # 프롬프트 구성
    fields_text = "\n".join([f"- {field}: {content}" for field, content in form_data.items() if content])
    
    # 길이 지침
    length_guidelines = {
        "표준 (기본 작성, 각 섹션당 2-3개의 문단)": "각 섹션당 2-3개의 문단으로 작성할 것. 균형 잡힌 내용과 적절한 상세 수준을 유지할 것.",
        "간략 (핵심 요약, 각 섹션당 1-2개의 문단)": "각 섹션당 1-2개의 간결한 문단으로 제한할 것. 핵심 요점만 포함하고 모든 불필요한 세부 사항은 제외할 것.",
        "상세 (심층 분석, 각 섹션당 3-4개의 문단)": "각 섹션을 3-5개의 문단으로 확장하여 깊이 있게 다룰 것. 배경 정보, 통계, 사례 연구 등 상세한 정보를 포함할 것."
    }
    
    selected_length_guideline = length_guidelines.get(options["length"], length_guidelines["표준 (기본 작성, 각 섹션당 2-3개의 문단)"])
    
    prompt = f"""
당장 보고서 작성해! 너는 지자체 보고서 작성 전문가로 내가 시키는 대로 정확하게 작업할 거야.

## 서식 준수 - 절대 어기지 마!
내가 선택한 '{options["template_name"]}' 서식을 100% 그대로 따라야 해.
다음 순서대로 모든 섹션 하나도 빠짐없이 포함시켜: {fields_structure}

## 보고서 유형
{options["report_type"]}

## 보고서 서식
{options["template_name"]}

## 입력된 내용
{fields_text}

## 보고서 길이 요구사항
{selected_length_guideline}

## 작성 요구사항 - 반드시 준수!
1. 내가 입력한 정보는 그대로 활용하되, 부족한 부분은 네가 채워넣어.
2. 내가 제공한 서식 구조({fields_structure})는 절대 변경하지 마! 하나라도 빠지면 안 돼.
3. 입력 내용이 없는 섹션도 반드시 작성해서 완성된 보고서를 만들어.
4. 내가 내용을 거의 입력하지 않아도 네가 알아서 전문적인 내용으로 채워넣어야 해.
5. 공문서에 맞는 전문 용어와 공식적인 어투 사용해.
6. 마크다운으로 작성하되, 제목은 H1(#), 섹션은 H2(##)로 할 것.
7. 필요하면 표와 목록을 활용해서 정보를 명확하게 전달해.
8. 간결하고 명확한 문장으로 작성할 것.
9. 객관적이고 사실에 근거한 내용으로 채울 것.
10. 전문적이고 개조식으로 표현할 것. (예: '~함', '~해야 함', '~필요함', '~중요함')
11. 모든 내용을 개조식 형태로 작성하고, 문장 마지막은 '~이다', '~한다'가 아닌 '~임', '~함' 등으로 끝내야 함.
12. 절대로 서술형 문장(~합니다, ~됩니다 등)을 사용하지 말 것.

엄격하게 서식 구조를 따라야 해. 내가 제목만 주더라도 모든 섹션({fields_structure})을 빠짐없이 포함한 완벽한 보고서를 작성해! 네가 마음대로 섹션을 추가하거나 삭제하는 것은 용납 못 해.

마크다운 형식으로만 반환하고, 다른 설명이나 소개는 일절 포함하지 마!
"""
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                    generation_config={"temperature": temperature})
        
        # 시스템 지시사항 추가 (Gemini의 경우 별도로 설정)
        system_instruction = "당신은 전문적인 보고서를 작성하는 AI 조수입니다. 반드시 개조식 문체(~함, ~임, ~해야 함 등)로만 작성하세요. 서술형(~합니다, ~됩니다)은 절대 사용하지 마세요."
        
        response = model.generate_content([
            {"role": "user", "parts": [system_instruction]},
            {"role": "model", "parts": ["네, 개조식 문체로만 작성하겠습니다."]},
            {"role": "user", "parts": [prompt]}
        ])
        
        # 응답 받기
        result = response.text
        
        # 서술형 문장이 있는지 확인하고, 있다면 개조식으로 변환 시도
        if '습니다' in result or '니다' in result:
            correction_prompt = f"""
다음 보고서를 완전한 개조식으로 다시 작성해주세요. 
모든 문장을 '~함', '~임', '~필요함', '~중요함' 등의 형태로 바꿔주세요.
서술형('~합니다', '~됩니다', '~습니다' 등)은 절대 사용하지 마세요.

{result}
"""
            correction_response = model.generate_content(correction_prompt)
            result = correction_response.text
        
        return result
        
    except Exception as e:
        st.error(f"보고서 생성 중 오류가 발생했습니다: {str(e)}")
        if "api_key" in str(e).lower():
            st.error("Gemini API 키가 올바르게 설정되어 있는지 확인하세요.")
        return None
