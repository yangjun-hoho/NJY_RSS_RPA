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
    
    # 내용이 있는 필드만 추출
    filled_fields = {field: content for field, content in form_data.items() if content.strip()}
    
    # 프롬프트 구성
    fields_text = "\n".join([f"- {field}: {content}" for field, content in filled_fields.items()])
    
    # 보고서 유형별 특화 지침
    report_type_guidelines = {
        "계획 보고서": """
- 미래지향적 관점에서 작성
- 구체적이고 현실적인 추진 방안 제시
- 정량적 목표와 성과지표 반드시 포함
- 단계별 추진 일정과 예산배분 계획 상세 기술
- SWOT 분석을 통한 전략적 접근법 제시
- 각 단계별 성공기준 명확히 설정
- 법적/제도적 근거 인용 시 정확한 출처 명시
- 사업의 지속가능성 및 확장성 강조""",
        
        "대책 보고서": """
- 문제 상황의 심각성과 긴급성 강조
- 정확한 현황 분석과 데이터 기반 문제 진단
- 근본 원인과 파생 문제 체계적 분석
- 단기/중기/장기 대책 구분하여 제시
- 예상 장애요소와 극복방안 함께 제시
- 유사 사례의 성공/실패 요인 분석 포함
- 조치 우선순위와 이행 로드맵 구체화
- 효과 검증 방안 및 평가지표 명시""",
        
        "상황 보고서": """
- 사실에 기반한 객관적 정보 전달
- 시간 순서에 따른 체계적 상황 전개 기술
- 주요 이해관계자와 영향 범위 명확히 설명
- 데이터와 통계를 활용한 상황 심각성 전달
- 기존 조치사항과 효과성 평가 포함
- 후속 상황 예측 및 시나리오별 대응방안 제시
- 정보 출처와 확인 경로 명시
- 의사결정 지원을 위한 핵심사항 요약제시""",
        
        "분석 보고서": """
- 명확한 분석 목적과 범위 설정
- 데이터 수집 방법론과 표본 특성 상세 기술
- 다양한 분석 기법 활용 (정량/정성 분석 병행)
- 인과관계와 상관관계 구분하여 해석
- 시계열 추이 분석 및 미래 예측 포함
- 시각적 자료(그래프, 차트 등)를 활용한 결과 표현
- 대안적 해석 가능성과 한계점 명시
- 실행 가능한 권고사항 도출""",
        
        "기타 보고서": """
- 명확한 목적성과 핵심 메시지 강조
- 간결하면서도 필수 정보 누락 없이 작성
- 객관적 사실과 주관적 의견 명확히 구분
- 시간, 장소, 관계자 등 5W1H 원칙 준수
- 우선순위에 따른 내용 배치
- 의사결정에 필요한 핵심정보 강조
- 후속조치 사항 구체적 명시
- 관련 참고자료 및 출처 명확히 제시"""
    }
    
    # 길이 지침
    length_guidelines = {
        "표준 (기본 작성, 각 섹션당 2-3개의 문단)": """
- 각 섹션당 2-3개의 문단 구성
- 핵심 내용을 중심으로 논리적 전개
- 항목별 3-5개의 요점 포함
- 균형 잡힌 내용과 적절한 상세 수준 유지
- 필요 시 간단한 표나 목록 활용""",
        
        "간략 (핵심 요약, 각 섹션당 1-2개의 문단)": """
- 각 섹션을 1-2개의 간결한 문단으로 제한
- 핵심 요점만 포함하고 불필요한 상세 내용 제외
- 항목별 2-3개의 핵심 요점만 명시
- 전체 보고서 분량 A4 2장 이내로 압축
- 시각적 요소 최소화하고 텍스트 중심으로 구성""",
        
        "상세 (심층 분석, 각 섹션당 3-4개의 문단)": """
- 각 섹션을 3-5개의 상세 문단으로 구성
- 배경 정보, 통계, 사례 연구 등 심층적 내용 포함
- 항목별 5-7개의 세부 요점 기술
- 다양한 시각적 자료(표, 그래프, 다이어그램 등) 적극 활용
- 관련 법규, 사례, 전문가 의견 등 참고자료 인용
- 각 주제별 다양한 관점과 가능성 검토"""
    }
    
    # 보고서 유형별 특화 예시 문구
    examples_by_type = {
        "계획 보고서": {
            "배경": [
                "- 지역 내 청년 실업률 전년 대비 15% 증가, 대책 마련 시급",
                "- 청년창업지원센터 건립 관련 주민 요구 지속적으로 증가",
                "- 국가 청년정책 5개년 계획과 연계한 지역 맞춤형 전략 부재",
                "- 기존 청년지원사업의 분절적 운영으로 통합적 지원체계 필요"
            ],
            "목적": [
                "- 지역 청년의 안정적 정착 및 일자리 창출 기반 마련",
                "- 청년 친화형 산업 생태계 조성을 통한 지역경제 활성화",
                "- 수요자 중심의 맞춤형 청년 지원 프로그램 개발·운영",
                "- 청년의 지역사회 참여 확대 및 사회적 역량 강화"
            ],
            "추진계획": [
                "- 1단계('25.4~6월): 청년정책협의체 구성 및 실태조사 실시",
                "- 2단계('25.7~9월): 청년일자리 허브센터 조성 및 프로그램 개발",
                "- 3단계('25.10~12월): 청년 창업지원 특화 프로그램 시범 운영",
                "- 4단계('26.1~3월): 성과평가 및 확대 운영방안 수립"
            ]
        },
        "대책 보고서": {
            "문제점": [
                "- 최근 3년간 도심 지역 침수피해 연평균 27% 증가",
                "- 노후 하수관로 비율 38%로 집중호우 시 배수 용량 한계 노출",
                "- 우수저류시설 부족으로 첨두유출량 제어 역량 미흡",
                "- 재난대응 매뉴얼 현행화 미비 및 부서 간 협업체계 미흡"
            ],
            "대책": [
                "- 하수관로 정비사업 5개년 계획 수립 및 1단계 사업 즉시 착수",
                "- 도심 지하 유휴공간 활용한 우수저류시설 5개소 신규 확보",
                "- 빗물펌프장 증설(2개소) 및 기존 시설 용량 개선(4개소)",
                "- 재난대응 통합관제시스템 구축 및 유관기관 실시간 정보공유체계 마련"
            ]
        },
        "상황 보고서": {
            "현재상태": [
                "- 태풍 '미래' 북상에 따른 시간당 최대 강수량 85mm 기록",
                "- 시 남부지역 4개 행정동 침수피해 발생, 이재민 213세대 발생",
                "- 주요 간선도로 3개소 통행 제한 조치 시행 중",
                "- 시 재난안전대책본부 2단계 비상 발령 및 24시간 비상근무체계 가동"
            ],
            "조치사항": [
                "- 침수지역 배수펌프 12대 긴급 투입 및 배수작업 진행 중",
                "- 이재민 임시주거시설 3개소 운영, 구호물품 및 재난지원금 지급 준비",
                "- 응급복구반 10개조 편성·투입, 도로 잔해물 제거 및 안전시설물 복구",
                "- 상황전파시스템 가동, 시민 대상 재난문자 6회 발송"
            ]
        },
        "분석 보고서": {
            "분석결과": [
                "- 공공도서관 이용률, 인구밀집지역 대비 외곽지역 30% 낮음",
                "- 이용자 만족도 조사 결과, 프로그램 다양성(37%)과 접근성(29%) 개선 요구 가장 높음",
                "- 연령별 이용패턴 분석 결과, 청소년·노년층 특화 프로그램 수요 증가세",
                "- 디지털 콘텐츠 이용률, 전년 대비 42% 증가했으나 관련 인프라 부족"
            ],
            "시사점": [
                "- 지역 간 문화 인프라 격차 해소를 위한 균형 발전 전략 필요",
                "- 생애주기별 맞춤형 프로그램 개발·운영으로 이용자층 다변화 도모",
                "- 디지털 전환에 대응한 스마트 도서관 인프라 확충 시급",
                "- 지역 문화공간으로서 도서관 역할 강화 위한 복합문화시설화 검토"
            ]
        },
        "기타 보고서": {
            "주요내용": [
                "- 시청 민원실 환경개선 사업 1차 완료, 이용자 편의성 30% 향상",
                "- 무인민원발급기 신규 설치(3대) 및 노후장비 교체(5대) 완료",
                "- 민원처리 신속성 향상을 위한 '원스톱 민원처리시스템' 구축 중",
                "- 직원 역량강화 교육 시행(32명 이수) 및 민원응대 매뉴얼 개정"
            ],
            "특이사항": [
                "- 디지털취약계층 지원을 위한 '민원도우미' 인력 추가 배치 필요",
                "- 민원실 냉난방 시설 노후화로 교체 검토 요망",
                "- 통합민원관리시스템 오류 발생 빈도 증가, 기술지원 요청 중",
                "- 신규 민원서비스 홍보 부족으로 시민 인지도 저조"
            ]
        }
    }
    
    # 선택된 보고서 유형에 따른 지침과 예시 선택
    report_type_guideline = report_type_guidelines.get(options["report_type"], "")
    selected_length_guideline = length_guidelines.get(options["length"], length_guidelines["표준 (기본 작성, 각 섹션당 2-3개의 문단)"])
    
    # 예시 문구 선택 (보고서 유형에 따라)
    examples = examples_by_type.get(options["report_type"], {})
    examples_text = ""
    
    # 현재 템플릿에 있는 필드만 예시로 포함
    for field in all_fields:
        if field in examples:
            examples_text += f"\n{field} 예시:\n" + "\n".join(examples[field]) + "\n"
    
    # 자주 사용되는 행정 용어 및 표현 사전
    administrative_terms = """
## 행정 전문용어 및 표현 사전
- 시행: '실시'보다 '시행' 용어 사용 (예: 시범사업 시행)
- 추진: 계획적 진행 강조 시 사용 (예: 단계적 추진)
- 운영: 지속적 관리 표현 시 사용 (예: 프로그램 운영)
- 수립: 계획 작성 시 사용 (예: 종합계획 수립)
- 검토: 분석적 사고 표현 시 사용 (예: 타당성 검토)
- 강화: 기존 역량 향상 시 사용 (예: 협력체계 강화)
- 개선: 문제해결 표현 시 사용 (예: 제도 개선)
- 확충: 양적 증가 표현 시 사용 (예: 인프라 확충)
- 증진: 질적 향상 표현 시 사용 (예: 효율성 증진)
- 도모: 간접적 달성 표현 시 사용 (예: 상생발전 도모)
"""
    
    # 시스템 프롬프트 강화
    system_prompt = f"""당신은 정부 및 지방자치단체의 공문서 작성에 특화된 전문 AI 비서입니다.
공적 문서에 적합한, 정확하고 간결하며 객관적인 보고서를 작성합니다.

##보고서 작성 원칙
1. 반드시 개조식 문체만 사용할 것 (예: ~함, ~임, ~요함, ~필요함)
2. 서술형 문장(~합니다, ~됩니다, ~입니다) 절대 사용 금지
3. 문장은 간결하고 명확하게 핵심만 전달할 것
4. 객관적 사실과 데이터 중심으로 작성할 것
5. 논리적 구조와 일관성을 유지할 것
6. 행정용어와 전문용어를 적절히 활용할 것
7. 각 섹션은 핵심 키워드로 시작하는 개조식 문장으로 구성할 것
8. 내용의 우선순위를 고려하여 중요도 순으로 배치할 것

{administrative_terms}"""
    
    # 메인 프롬프트 최적화
    prompt = f"""
## 보고서 작성 요청
'{options["report_type"]}'의 '{options["template_name"]}' 형식 보고서 작성 요청

## 서식 구조 (변경 불가)
다음 순서와 제목을 정확히 따라 작성: {fields_structure}

## 입력된 내용
{fields_text}

## 보고서 유형별 특화 지침
{report_type_guideline}

## 보고서 길이 요구사항
{selected_length_guideline}

## 작성 참고 예시
{examples_text}

## 작성 요구사항
1. 제공된 서식({fields_structure}) 구조를 100% 준수하고, 각 섹션 누락 없이 작성
2. 사용자 입력 내용은 최대한 존중하되, 빈 섹션은 적절한 내용으로 전문적으로 보완
3. 모든 내용은 개조식(~함, ~임, ~필요함 등)으로만 작성하고 서술형 문장 절대 사용 금지
4. 각 섹션 시작은 핵심 키워드로 시작하는 명확한 개조식 문장으로 구성
5. 마크다운 형식 사용: 제목은 H1(#), 섹션은 H2(##)로 통일
6. 필요시 중요 정보는 굵게(**) 처리하고, 핵심 수치나 통계는 따옴표로 강조
7. 관련 법규, 조례, 상위계획 등 근거 인용 시 출처 명확히 표기
8. 단계별/시간순 내용은 번호나 기호 사용하여 구조화
9. 예산, 통계, 비율 등 수치 데이터는 구체적이고 현실적으로 제시
10. 전체적으로 일관된 어조와 표현 방식 유지

## 마크다운 형식으로만 반환하고, 다른 설명이나 부가설명 없이 완성된 보고서만 제공할 것
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # 최적의 결과를 위해 GPT-4o 사용
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
- 모든 서술형 문장(~합니다, ~됩니다, ~습니다 등)을 개조식(~함, ~임, ~필요함 등)으로 변환
- 문장의 의미와 전문성은 유지
- 각 항목의 논리적 구조와 내용은 보존
- 마크다운 형식은 그대로 유지

보고서:
{result}
"""
            correction_response = client.chat.completions.create(
                model="gpt-4o",
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
    
    # 내용이 있는 필드만 추출
    filled_fields = {field: content for field, content in form_data.items() if content.strip()}
    
    # 프롬프트 구성
    fields_text = "\n".join([f"- {field}: {content}" for field, content in filled_fields.items()])
    
    # 보고서 유형별 작성 지침
    report_type_guidelines = {
        "계획 보고서": """
## 계획 보고서 작성 핵심 지침
- 중장기적 관점 포함한 종합적 계획 수립
- 정책적 연계성 및 상위계획과의 정합성 확보
- 추진 단계별 로드맵과 마일스톤 명확히 설정
- 소요예산 산출근거 및 재원조달 방안 구체화
- 성과지표 및 평가체계 사전 설계
- 실행가능성 및 지속가능성 중점 검토
- 관련 부서・기관 간 협업체계 명시
- 위험요소 및 대응방안 사전 검토
- 주요 이해관계자 분석 및 의견수렴 결과 반영""",
        
        "대책 보고서": """
## 대책 보고서 작성 핵심 지침
- 문제 상황의 심각성 및 시급성 명확히 전달
- 문제의 원인과 영향 범위 체계적 분석
- 실현가능한 대안 및 해결방안 제시
- 즉시 대응과 중장기 대책 구분하여 제시
- 대책별 기대효과 및 한계점 함께 제시
- 대책 이행 우선순위 및 단계적 접근법 제시
- 관계기관 협력방안 및 역할분담 명확화
- 예산・인력・법제도 등 필요 자원 명시
- 추진상황 모니터링 및 환류체계 설계""",
        
        "상황 보고서": """
## 상황 보고서 작성 핵심 지침
- 객관적 사실관계 중심의 명확한 정보 전달
- 시간 흐름에 따른 상황 전개 체계적 정리
- 피해 규모 및 영향 범위 정량적 서술
- 조치사항 및 대응현황 단계별 상세 기술
- 가용 자원 현황 및 추가 필요사항 명시
- 예상 전개상황 및 위험요소 선제적 파악
- 의사결정권자 참고용 핵심사항 요약 제시
- 언론・민원 대응 시 유의사항 포함
- 유관기관 정보공유 및 협조체계 명시""",
        
        "분석 보고서": """
## 분석 보고서 작성 핵심 지침
- 명확한 분석 목적과 방법론 제시
- 객관적 데이터 기반의 현황 분석
- 정량・정성 분석의 균형적 활용
- 다각적 관점에서의 문제 분석
- 비교분석 및 기준점(벤치마크) 활용
- 추세 및 패턴 분석을 통한 예측 제시
- 핵심 발견사항 및 시사점 강조
- 분석의 한계 및 고려사항 명시
- 정책적 함의 및 실행 가능한 제언 도출""",
        
        "기타 보고서": """
## 기타 보고서 작성 핵심 지침
- 보고 목적에 맞는 핵심 정보 선별 제시
- 5W1H 원칙에 따른 사실관계 명확화
- 간결하고 명확한 정보 전달 지향
- 우선순위에 따른 내용 구성
- 후속조치 및 참고사항 구체화
- 의사결정 지원을 위한 정보 구조화
- 객관적 사실과 주관적 의견 구분 표기
- 관련 근거자료 및 참고문헌 명시"""
    }
    
    # 보고서 유형별 유용 표현 사전
    expression_dictionaries = {
        "계획 보고서": """
## 계획 보고서 유용 표현
- "중장기 발전계획과 연계하여 단계적 추진 필요"
- "정책 실효성 제고를 위한 제도적 기반 마련 중점"
- "지속가능한 성장 동력 확보 차원에서 접근 필요"
- "사업의 선택과 집중을 통한 효율적 자원 배분 강조"
- "부서 간 유기적 협업체계 구축으로 시너지 효과 창출"
- "선도사업 우선 추진 후 성과에 따른 확산 전략 수립"
- "주민 참여형 거버넌스 구축으로 사업 추진동력 확보"
- "재정 건전성을 고려한 단계적 투자계획 수립 필요"
- "성과지표 중심의 관리체계 구축으로 책임성 강화"
- "리스크 요인 선제적 파악 및 대응방안 마련 중요"
        """,
        "대책 보고서": """
## 대책 보고서 유용 표현
- "심각성과 시급성을 고려한 즉시 대응 필요"
- "근본 원인 해소를 위한 구조적 접근 중요"
- "단기 대응과 중장기 해소방안 병행 추진"
- "부작용 최소화 관점에서 단계적 접근 필요"
- "유관기관 협업을 통한 종합적 대응체계 구축"
- "선제적 예방조치와 사후관리 균형 확보"
- "피해 최소화를 위한 우선순위 설정 중요"
- "현장 중심의 실질적 해결방안 마련 시급"
- "지속가능한 관리체계 구축으로 재발 방지"
- "대응 매뉴얼 구체화로 위기대응 역량 강화"
        """,
        "상황 보고서": """
## 상황 보고서 유용 표현
- "현재까지 파악된 주요 상황은 다음과 같음"
- "시간대별 조치사항 및 대응현황 정리"
- "인명・재산 피해 최소화 위한 긴급조치 시행"
- "유관기관 협조체계 가동, 공동대응 중"
- "상황 악화 가능성에 대비한 단계별 대응계획 마련"
- "실시간 모니터링 체계 구축으로 상황관리 강화"
- "주민 불안 해소를 위한 정보제공 채널 다각화"
- "2차 피해 방지를 위한 안전조치 우선 시행"
- "복구 우선순위 설정 및 자원배분 계획 수립"
- "향후 유사사례 재발 방지를 위한 제도개선 검토"
        """,
        "분석 보고서": """
## 분석 보고서 유용 표현
- "데이터 기반 현황 분석 결과, 주요 문제점 도출"
- "정량・정성 분석 병행으로 다각적 접근 시도"
- "시계열 추이 분석 통해 중장기 변화 양상 파악"
- "벤치마킹 사례와의 격차 분석 통해 개선점 도출"
- "상관관계 분석 통해 핵심 영향요인 식별"
- "SWOT 분석 기반 전략적 대응방향 설정"
- "비용-효과 분석 통해 최적 대안 선정 근거 마련"
- "다차원 요인 분석으로 복합적 원인구조 규명"
- "이해관계자 분석 통해 정책 수용성 제고방안 도출"
- "시나리오 분석 통해 미래 예측 및 대비책 마련"
        """,
        "기타 보고서": """
## 기타 보고서 유용 표현
- "핵심 사항을 중심으로 간략히 정리"
- "주요 경과 및 현안사항 위주 보고"
- "긴급 조치가 필요한 사항을 우선 보고"
- "의사결정 필요사항에 대한 검토의견 첨부"
- "실무진 차원의 대응현황 및 한계점 정리"
- "관련 부서 간 이견사항 및 조정 필요사항 명시"
- "제도적 개선이 필요한 문제점 별도 정리"
- "향후 조치계획 및 일정 구체화하여 제시"
- "참고자료 및 상세 데이터는 별도 첨부"
- "주요 위험요소 및 관리방안 사전 보고"
        """
    }
    
    # 길이 지침
    length_guidelines = {
        "표준 (기본 작성, 각 섹션당 2-3개의 문단)": """
## 표준 분량 작성 지침
- 각 섹션당 핵심 항목 3-5개 포함
- 항목별 2-3개의 세부 요점 기술
- 핵심 사항을 중심으로 명료하게 전개
- 필요시 간단한 도표나 그림 1-2개 포함
- 불필요한 부연설명 최소화
- 전체 균형감을 고려한 분량 배분
        """,
        "간략 (핵심 요약, 각 섹션당 1-2개의 문단)": """
## 간략 보고서 작성 지침
- 각 섹션당 핵심 항목 2-3개로 제한
- 항목별 핵심 메시지 1-2개로 집약
- 통계・수치 등 핵심 데이터 중심 구성
- 시각적 요소 최소화하고 텍스트 위주 간결 작성
- 전체 보고서 A4 2장 이내로 압축
- 보충 설명이 필요한 내용은 별첨 참고자료로 구성
        """,
        "상세 (심층 분석, 각 섹션당 3-4개의 문단)": """
## 상세 보고서 작성 지침
- 각 섹션당 5-7개 항목으로 상세 전개
- 항목별 다양한 관점 및 고려사항 포함
- 통계, 사례, 벤치마킹 등 다양한 근거 제시
- 표, 그래프, 다이어그램 등 시각적 자료 적극 활용
- 반대 의견이나 대안적 시각도 균형있게 포함
- 주요 쟁점에 대한 심층 분석 및 다각적 검토 제공
        """
    }
    
    # 보고서 유형별 특화 예시 문구
    examples_by_type = {
        "계획 보고서": {
            "배경": [
                "- 지역 내 청년 실업률 전년 대비 15% 증가, 대책 마련 시급",
                "- 청년창업지원센터 건립 관련 주민 요구 지속적으로 증가",
                "- 국가 청년정책 5개년 계획과 연계한 지역 맞춤형 전략 부재",
                "- 기존 청년지원사업의 분절적 운영으로 통합적 지원체계 필요"
            ],
            "목적": [
                "- 지역 청년의 안정적 정착 및 일자리 창출 기반 마련",
                "- 청년 친화형 산업 생태계 조성을 통한 지역경제 활성화",
                "- 수요자 중심의 맞춤형 청년 지원 프로그램 개발·운영",
                "- 청년의 지역사회 참여 확대 및 사회적 역량 강화"
            ],
            "추진계획": [
                "- 1단계('25.4~6월): 청년정책협의체 구성 및 실태조사 실시",
                "- 2단계('25.7~9월): 청년일자리 허브센터 조성 및 프로그램 개발",
                "- 3단계('25.10~12월): 청년 창업지원 특화 프로그램 시범 운영",
                "- 4단계('26.1~3월): 성과평가 및 확대 운영방안 수립"
            ]
        },
        "대책 보고서": {
            "문제점": [
                "- 최근 3년간 도심 지역 침수피해 연평균 27% 증가",
                "- 노후 하수관로 비율 38%로 집중호우 시 배수 용량 한계 노출",
                "- 우수저류시설 부족으로 첨두유출량 제어 역량 미흡",
                "- 재난대응 매뉴얼 현행화 미비 및 부서 간 협업체계 미흡"
            ],
            "대책": [
                "- 하수관로 정비사업 5개년 계획 수립 및 1단계 사업 즉시 착수",
                "- 도심 지하 유휴공간 활용한 우수저류시설 5개소 신규 확보",
                "- 빗물펌프장 증설(2개소) 및 기존 시설 용량 개선(4개소)",
                "- 재난대응 통합관제시스템 구축 및 유관기관 실시간 정보공유체계 마련"
            ]
        },
        "상황 보고서": {
            "현재상태": [
                "- 태풍 '미래' 북상에 따른 시간당 최대 강수량 85mm 기록",
                "- 시 남부지역 4개 행정동 침수피해 발생, 이재민 213세대 발생",
                "- 주요 간선도로 3개소 통행 제한 조치 시행 중",
                "- 시 재난안전대책본부 2단계 비상 발령 및 24시간 비상근무체계 가동"
            ],
            "조치사항": [
                "- 침수지역 배수펌프 12대 긴급 투입 및 배수작업 진행 중",
                "- 이재민 임시주거시설 3개소 운영, 구호물품 및 재난지원금 지급 준비",
                "- 응급복구반 10개조 편성·투입, 도로 잔해물 제거 및 안전시설물 복구",
                "- 상황전파시스템 가동, 시민 대상 재난문자 6회 발송"
            ]
        },
        "분석 보고서": {
            "분석결과": [
                "- 공공도서관 이용률, 인구밀집지역 대비 외곽지역 30% 낮음",
                "- 이용자 만족도 조사 결과, 프로그램 다양성(37%)과 접근성(29%) 개선 요구 가장 높음",
                "- 연령별 이용패턴 분석 결과, 청소년·노년층 특화 프로그램 수요 증가세",
                "- 디지털 콘텐츠 이용률, 전년 대비 42% 증가했으나 관련 인프라 부족"
            ],
            "시사점": [
                "- 지역 간 문화 인프라 격차 해소를 위한 균형 발전 전략 필요",
                "- 생애주기별 맞춤형 프로그램 개발·운영으로 이용자층 다변화 도모",
                "- 디지털 전환에 대응한 스마트 도서관 인프라 확충 시급",
                "- 지역 문화공간으로서 도서관 역할 강화 위한 복합문화시설화 검토"
            ]
        },
        "기타 보고서": {
            "주요내용": [
                "- 시청 민원실 환경개선 사업 1차 완료, 이용자 편의성 30% 향상",
                "- 무인민원발급기 신규 설치(3대) 및 노후장비 교체(5대) 완료",
                "- 민원처리 신속성 향상을 위한 '원스톱 민원처리시스템' 구축 중",
                "- 직원 역량강화 교육 시행(32명 이수) 및 민원응대 매뉴얼 개정"
            ],
            "특이사항": [
                "- 디지털취약계층 지원을 위한 '민원도우미' 인력 추가 배치 필요",
                "- 민원실 냉난방 시설 노후화로 교체 검토 요망",
                "- 통합민원관리시스템 오류 발생 빈도 증가, 기술지원 요청 중",
                "- 신규 민원서비스 홍보 부족으로 시민 인지도 저조"
            ]
        }
    }
    
    # 선택된 보고서 유형에 따른 지침과 예시 선택
    report_type_guideline = report_type_guidelines.get(options["report_type"], "")
    selected_length_guideline = length_guidelines.get(options["length"], length_guidelines["표준 (기본 작성, 각 섹션당 2-3개의 문단)"])
    
    # 선택된 표현 사전
    expression_dictionary = expression_dictionaries.get(options["report_type"], "")
    
    # 예시 문구 선택 (보고서 유형에 따라)
    examples = examples_by_type.get(options["report_type"], {})
    examples_text = ""
    
    # 현재 템플릿에 있는 필드만 예시로 포함
    for field in all_fields:
        if field in examples:
            examples_text += f"\n{field} 예시:\n" + "\n".join(examples[field]) + "\n"
    
    # 행정 용어 및 표현 사전
    administrative_terms = """
## 행정 보고서 핵심 용어 및 표현 사전
- 시행: 계획의 실제 실행 (예: "사업 시행")
- 추진: 목표를 향한 지속적 진행 (예: "사업 추진")
- 수립: 계획을 세움 (예: "대책 수립")
- 이행: 의무나 약속을 실행함 (예: "의무 이행")
- 도모: 어떤 상태나 결과를 이루고자 함 (예: "발전 도모")
- 강구: 방법이나 대책을 찾음 (예: "방안 강구")
- 검토: 살펴보고 생각함 (예: "타당성 검토")
- 제고: 수준이나 가치를 높임 (예: "효율성 제고")
- 지양: 바람직하지 않아 하지 않음 (예: "과잉대응 지양")
- 지향: 목표로 삼아 나아감 (예: "혁신 지향")
- 조치: 어떤 일을 처리함 (예: "시정 조치")
- 조성: 환경이나 분위기를 만듦 (예: "여건 조성")
- 구축: 체계적으로 세움 (예: "시스템 구축")
- 확보: 필요한 것을 마련함 (예: "예산 확보")
- 정비: 체계적으로 정돈함 (예: "제도 정비")
- 강화: 더 강하게 함 (예: "기능 강화")
- 증진: 점점 나아지게 함 (예: "복지 증진")

## 개조식 문장 작성 패턴
- 핵심 키워드로 시작: "현황 분석 결과, ..." / "제도개선 필요성 검토 결과, ..."
- 간결한 정보 전달: "시민 만족도 85% 달성" / "사업비 10억원 투입 예정"
- 객관적 사실 기술: "민원 접수건수 전년대비 15% 증가" / "예산집행률 92% 기록" 
- 추진 방향 제시: "시민 참여 중심 정책 설계 필요" / "단계별 추진으로 리스크 최소화 중요"
- 결론 도출: "종합적인 개선대책 마련 시급" / "장기적 관점의 정책 재설계 요구됨"
"""
    
    # 메인 프롬프트 최적화
    prompt = f"""
## 보고서 작성 요청
정부/지자체 공식 '{options["report_type"]}'의 '{options["template_name"]}' 형식으로 작성 요청

## 서식 구조 (절대 변경 불가)
다음 순서와 제목을 정확히 따라 작성: {fields_structure}

## 입력된 내용
{fields_text}

## 보고서 유형별 특화 지침
{report_type_guideline}

## 행정 용어 및 표현 가이드
{administrative_terms}

## 보고서 길이 요구사항
{selected_length_guideline}

## 참고 표현 사전
{expression_dictionary}

## 작성 참고 예시
{examples_text}

## 작성 요구사항 (반드시 준수)
1. 제공된 서식({fields_structure}) 구조를 100% 준수하고, 각 섹션을 누락 없이 작성할 것
2. 사용자 입력 내용은 최대한 존중하되, 빈 섹션은 적절한 내용으로 전문적으로 보완할 것
3. 모든 내용은 반드시 개조식(~함, ~임, ~필요함 등)으로만 작성하고 서술형 문장(~합니다, ~됩니다 등) 절대 사용 금지
4. 각 항목은 핵심 키워드로 시작하는 간결하고 명확한 문장으로 구성할 것
5. 마크다운 형식 사용: 제목은 H1(#), 섹션은 H2(##)로 통일할 것
6. 필요시 중요 정보는 굵게(**) 처리하고, 핵심 수치나 통계는 따옴표로 강조할 것
7. 보고서의 전체 논리 구조와 일관성을 유지할 것
8. 단계별/시간순 내용은 번호나 기호 사용하여 구조화할 것
9. 예산, 통계, 비율 등 구체적 수치 활용하여 객관성 강화할 것
10. 행정 보고서에 적합한 전문 용어와 표현을 적절히 활용할 것

## 마크다운 형식으로만 반환하고, 다른 설명이나 부가설명 없이 완성된 보고서만 제공할 것
"""
    
    try:
        # 시스템 지시사항 추가 (Gemini의 경우 별도로 설정)
        system_instruction = """당신은 정부 및 지방자치단체의 공문서 작성에 특화된 전문 AI 비서입니다.
공적 문서에 적합한, 정확하고 간결하며 객관적인 보고서를 작성합니다.

##보고서 작성 원칙
1. 반드시 개조식 문체만 사용할 것 (예: ~함, ~임, ~요함, ~필요함)
2. 서술형 문장(~합니다, ~됩니다, ~입니다) 절대 사용 금지
3. 문장은 간결하고 명확하게 핵심만 전달할 것
4. 객관적 사실과 데이터 중심으로 작성할 것
5. 논리적 구조와 일관성을 유지할 것
6. 행정용어와 전문용어를 적절히 활용할 것
7. 각 섹션은 핵심 키워드로 시작하는 개조식 문장으로 구성할 것
8. 내용의 우선순위를 고려하여 중요도 순으로 배치할 것"""

        # Gemini 모델 구성
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            generation_config=generation_config
        )
        
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
- 모든 서술형 문장(~합니다, ~됩니다, ~습니다 등)을 개조식(~함, ~임, ~필요함 등)으로 변환
- 문장의 의미와 전문성은 유지
- 각 항목의 논리적 구조와 내용은 보존
- 마크다운 형식은 그대로 유지

보고서:
{result}
"""
            correction_response = model.generate_content([
                {"role": "user", "parts": [system_instruction]},
                {"role": "model", "parts": ["네, 개조식 문체로만 작성하겠습니다."]},
                {"role": "user", "parts": [correction_prompt]}
            ])
            
            result = correction_response.text
        
        return result
        
    except Exception as e:
        st.error(f"보고서 생성 중 오류가 발생했습니다: {str(e)}")
        if "api_key" in str(e).lower():
            st.error("Gemini API 키가 올바르게 설정되어 있는지 확인하세요.")
        return None