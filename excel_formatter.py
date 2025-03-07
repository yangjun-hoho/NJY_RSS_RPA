



import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import tempfile
import re
import time
import json
from datetime import datetime, date
import openai
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# API 키 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# JSON 직렬화를 위한 사용자 정의 인코더
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, pd.Timestamp)):
            return str(obj)
        elif pd.isna(obj):
            return None
        return super().default(obj)

def run():
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
    /* 데이터프레임 스타일 */
    .dataframe-container {
        border: 1px solid #e6e6e6;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

    # API 키 확인
    if not OPENAI_API_KEY or not GEMINI_API_KEY:
        st.error("API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY와 GEMINI_API_KEY를 설정해주세요.")
        st.stop()

    # 세션 상태 초기화
    if "source_df" not in st.session_state:
        st.session_state.source_df = None
    if "template_df" not in st.session_state:
        st.session_state.template_df = None
    if "result_df" not in st.session_state:
        st.session_state.result_df = None
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "mapping_details" not in st.session_state:
        st.session_state.mapping_details = None

    # 타이틀 및 설명
    st.title("📊 AI 기반 엑셀 정리하기")
    st.caption("원본 데이터와 제출 양식을 업로드하면 AI가 분석하여 형식에 맞게 데이터를 정리해 드립니다.")

    # 사이드바 설정
    with st.sidebar:
        st.divider()
        # AI 모델 선택
        model_provider = st.radio(
            "🤖 AI모델 선택",
            ["OpenAI GPT-4o", "Google Gemini-2.0"],
            help="데이터 분석 및 매핑에 사용할 AI 모델을 선택하세요."
        )
        
        # 공통 설정
        temperature = st.slider("⚙️ 창의성 수준", min_value=0.0, max_value=1.0, value=0.3, step=0.1,
                             help="낮은 값은 일관된 결과를, 높은 값은 다양한 해석을 제공합니다.")
        
        # 매핑 방식 설정
        mapping_method = st.radio(
            "매핑 방식",
            ["자동 (AI 기반)", "수동 (열 이름 선택)"],
            help="자동은 AI가 열을 분석하여 매핑합니다. 수동은 사용자가 직접 매핑합니다."
        )
        
        # 고급 설정 (확장 가능)
        with st.expander("고급 설정"):
            handle_missing = st.radio(
                "누락된 데이터 처리",
                ["공백으로 남김", "기본값 사용", "유사 데이터로 예측"],
                help="필수 열에 데이터가 없을 때 처리 방법을 선택하세요."
            )
            
            validate_data = st.checkbox(
                "데이터 유효성 검사",
                value=True,
                help="결과 데이터의 타입과 형식이 올바른지 확인합니다."
            )
        
        st.divider()
        st.caption("© 2025 남양주시 AI 엑셀 정리 도구")

    # 파일 업로드 영역
    st.subheader("데이터 파일 업로드")
    
    # 두 개의 파일 업로더를 나란히 배치
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**원본 데이터 파일**")
        source_file = st.file_uploader(
            "정리가 필요한 데이터 파일을 업로드하세요",
            type=["xlsx", "xls", "csv"],
            key="source_uploader",
            help="정리가 필요한 원본 데이터 파일을 업로드하세요."
        )
        
        if source_file:
            try:
                # 파일 확장자에 따라 다르게 처리
                if source_file.name.endswith('.csv'):
                    st.session_state.source_df = pd.read_csv(source_file)
                else:
                    st.session_state.source_df = pd.read_excel(source_file)
                
                st.success(f"원본 데이터 로드 완료: {st.session_state.source_df.shape[0]}행 × {st.session_state.source_df.shape[1]}열")
            except Exception as e:
                st.error(f"원본 파일 로드 오류: {str(e)}")
    
    with col2:
        st.markdown("**제출 양식 파일**")
        template_file = st.file_uploader(
            "제출 양식 파일을 업로드하세요",
            type=["xlsx", "xls", "csv"],
            key="template_uploader",
            help="데이터를 맞춰야 할 제출 양식 파일을 업로드하세요."
        )
        
        if template_file:
            try:
                # 파일 확장자에 따라 다르게 처리
                if template_file.name.endswith('.csv'):
                    st.session_state.template_df = pd.read_csv(template_file)
                else:
                    st.session_state.template_df = pd.read_excel(template_file)
                
                st.success(f"양식 파일 로드 완료: {st.session_state.template_df.shape[1]}개 열")
            except Exception as e:
                st.error(f"양식 파일 로드 오류: {str(e)}")
    
    # 파일 미리보기 영역
    if st.session_state.source_df is not None or st.session_state.template_df is not None:
        st.subheader("데이터 미리보기")
        
        preview_tabs = st.tabs(["원본 데이터", "제출 양식"])
        
        with preview_tabs[0]:
            if st.session_state.source_df is not None:
                st.dataframe(st.session_state.source_df.head(5), use_container_width=True)
                st.caption(f"총 {st.session_state.source_df.shape[0]}행, {st.session_state.source_df.shape[1]}열")
            else:
                st.info("원본 데이터 파일을 업로드해주세요.")
        
        with preview_tabs[1]:
            if st.session_state.template_df is not None:
                st.dataframe(st.session_state.template_df.head(2), use_container_width=True)
                st.caption(f"양식 필수 항목: {', '.join(st.session_state.template_df.columns.tolist())}")
            else:
                st.info("제출 양식 파일을 업로드해주세요.")
    
    # 수동 매핑 UI (매핑 방식이 수동일 때만 표시)
    if (mapping_method == "수동 (열 이름 선택)" and 
        st.session_state.source_df is not None and 
        st.session_state.template_df is not None):
        
        st.subheader("열 매핑 설정")
        st.markdown("원본 데이터의 각 열을 제출 양식의 어떤 열로 매핑할지 선택하세요.")
        
        # 수동 매핑을 위한 딕셔너리 초기화
        if "manual_mapping" not in st.session_state:
            st.session_state.manual_mapping = {}
        
        # 양식 열마다 대응하는 원본 열 선택 UI 생성
        manual_mapping_container = st.container()
        with manual_mapping_container:
            # 컬럼을 4개씩 그룹화하여 한 행에 표시
            template_columns = st.session_state.template_df.columns.tolist()
            source_columns = ["[매핑 안 함]"] + st.session_state.source_df.columns.tolist()
            
            # 4열씩 배치
            cols_per_row = 4
            for i in range(0, len(template_columns), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    idx = i + j
                    if idx < len(template_columns):
                        template_col = template_columns[idx]
                        with cols[j]:
                            st.session_state.manual_mapping[template_col] = st.selectbox(
                                f"→ {template_col}",
                                options=source_columns,
                                key=f"map_{template_col}"
                            )
    
    # 데이터 처리 버튼
    if (st.session_state.source_df is not None and 
        st.session_state.template_df is not None):
        
        process_btn = st.button(
            "데이터 정리하기", 
            type="primary", 
            use_container_width=True,
            help="AI를 사용하여 원본 데이터를 제출 양식에 맞게 정리합니다."
        )
        
        if process_btn:
            # 진행 상황 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 처리 과정 시작
            status_text.text("데이터 분석 중...")
            progress_bar.progress(20)
            
            # 데이터 매핑 처리
            if mapping_method == "자동 (AI 기반)":
                status_text.text("AI로 데이터 매핑 분석 중...")
                
                # AI 모델 선택에 따른 처리
                if model_provider == "OpenAI GPT-4o":
                    try:
                        mapping_result = analyze_with_openai(
                            st.session_state.source_df, 
                            st.session_state.template_df, 
                            temperature
                        )
                    except Exception as e:
                        st.error(f"OpenAI 처리 오류: {str(e)}")
                        mapping_result = None
                else:
                    try:
                        mapping_result = analyze_with_gemini(
                            st.session_state.source_df, 
                            st.session_state.template_df, 
                            temperature
                        )
                    except Exception as e:
                        st.error(f"Gemini 처리 오류: {str(e)}")
                        mapping_result = None
                
                if not mapping_result:
                    st.error("데이터 매핑에 실패했습니다. 수동 매핑을 시도하거나 파일을 확인해주세요.")
                    return
                
                # 매핑 결과 저장
                column_mapping = mapping_result.get("column_mapping", {})
                mapping_details = mapping_result.get("explanation", "")
                st.session_state.mapping_details = mapping_details
            else:
                # 수동 매핑 사용
                column_mapping = {}
                for template_col, source_col in st.session_state.manual_mapping.items():
                    if source_col != "[매핑 안 함]":
                        column_mapping[template_col] = source_col
                
                mapping_details = "수동으로 설정한 열 매핑을 사용했습니다."
                st.session_state.mapping_details = mapping_details
            
            progress_bar.progress(50)
            status_text.text("데이터 변환 중...")
            
            # 매핑을 기반으로 새 데이터프레임 생성
            try:
                result_df = create_mapped_dataframe(
                    st.session_state.source_df,
                    st.session_state.template_df,
                    column_mapping,
                    handle_missing
                )
                
                # 데이터 유효성 검사 (옵션에 따라)
                if validate_data:
                    status_text.text("데이터 유효성 검사 중...")
                    result_df = validate_dataframe(result_df, st.session_state.template_df)
                
                st.session_state.result_df = result_df
                st.session_state.processing_complete = True
                
                progress_bar.progress(100)
                status_text.text("처리 완료!")
                
                st.success("데이터 정리가 완료되었습니다!")
                
            except Exception as e:
                st.error(f"데이터 변환 오류: {str(e)}")
                progress_bar.progress(100)
                status_text.text("처리 실패")
    
    # 결과 표시 영역
    if st.session_state.processing_complete and st.session_state.result_df is not None:
        st.subheader("처리 결과")
        
        # 결과 탭 생성
        result_tabs = st.tabs(["결과 데이터", "매핑 상세 정보", "다운로드"])
        
        with result_tabs[0]:
            st.dataframe(st.session_state.result_df, use_container_width=True)
            st.caption(f"총 {st.session_state.result_df.shape[0]}행, {st.session_state.result_df.shape[1]}열")
        
        with result_tabs[1]:
            st.markdown("### 데이터 매핑 상세 정보")
            st.markdown(st.session_state.mapping_details)
        
        with result_tabs[2]:
            # 다운로드 옵션
            st.markdown("### 결과 파일 다운로드")
            download_format = st.radio(
                "다운로드 형식",
                options=["Excel (.xlsx)", "CSV (.csv)"],
                horizontal=True
            )
            
            # 버튼 행 (파일 이름 입력 및 다운로드 버튼)
            col1, col2 = st.columns([3, 1])
            
            with col1:
                file_name = st.text_input(
                    "파일 이름",
                    value="formatted_data",
                    placeholder="파일 이름을 입력하세요 (확장자 제외)"
                )
            
            with col2:
                if download_format == "Excel (.xlsx)":
                    buffer = io.BytesIO()
                    st.session_state.result_df.to_excel(buffer, index=False)
                    buffer.seek(0)
                    download_button = st.download_button(
                        label="다운로드",
                        data=buffer,
                        file_name=f"{file_name}.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )
                else:
                    download_button = st.download_button(
                        label="다운로드",
                        data=st.session_state.result_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"{file_name}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    # 사용 방법 안내
    st.markdown("---")
    st.markdown("""
    ### 💡 사용 방법
    
    1. **원본 데이터 파일**과 **제출 양식 파일**을 업로드하세요.
    2. 자동 매핑을 사용하거나 수동으로 열 매핑을 설정하세요.
    3. **데이터 정리하기** 버튼을 클릭하세요.
    4. 결과를 확인하고 원하는 형식으로 다운로드하세요.
    
    ### ✨ 특징
    
    - AI 기반 자동 데이터 열 매핑
    - 수동 열 매핑 옵션 지원
    - 데이터 유효성 검사
    - 다양한 파일 형식 지원 (Excel, CSV)
    """)

# OpenAI를 사용한 데이터 분석 및 매핑
def analyze_with_openai(source_df, template_df, temperature=0.3):
    """OpenAI GPT를 사용하여 데이터 분석 및 매핑"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 데이터프레임 복사
        source_df_copy = source_df.copy()
        template_df_copy = template_df.copy()
        
        # 데이터프레임 정보 준비 (날짜/시간 객체 등 JSON 직렬화 문제 해결)
        source_cols = source_df_copy.columns.tolist()
        
        # JSON 직렬화를 위해 사용자 정의 인코더 사용
        source_sample_dict = source_df_copy.head(3).to_dict(orient='records')
        source_sample = json.loads(json.dumps(source_sample_dict, cls=CustomJSONEncoder, ensure_ascii=False))
        
        template_cols = template_df_copy.columns.tolist()
        template_sample_dict = template_df_copy.head(1).to_dict(orient='records') if not template_df_copy.empty else {}
        template_sample = json.loads(json.dumps(template_sample_dict, cls=CustomJSONEncoder, ensure_ascii=False))
        
        # 프롬프트 생성
        system_prompt = """
        당신은 데이터 분석 전문가입니다. 원본 데이터와 제출 양식을 분석하여 최적의 열 매핑을 제안해야 합니다.
        데이터의 의미와 내용을 고려하여 가장 적합한 매핑을 찾으세요.
        일부 열은 직접 매핑되지 않을 수 있으며, 그런 경우 값을 조합하거나 변환해야 할 수 있습니다.
        """

        # 중괄호를 이스케이프하기 위해 중괄호를 두 번 사용
        user_prompt = f"""
        # 작업: 원본 데이터를 제출 양식에 맞게 매핑하기

        ## 원본 데이터 정보:
        - 열 목록: {source_cols}
        - 샘플 데이터: {json.dumps(source_sample, ensure_ascii=False, indent=2)}

        ## 제출 양식 정보:
        - 필수 열 목록: {template_cols}
        - 양식 샘플: {json.dumps(template_sample, ensure_ascii=False, indent=2)}

        ## 요청사항:
        1. 원본 데이터의 어떤 열이 제출 양식의 어떤 열에 매핑되어야 하는지 결정하세요.
        2. 일부 열은 직접적인 매핑이 없을 수 있으며 이 경우 적절한 기본값이나 변환 방법을 제안하세요.
        3. 데이터 타입과 형식을 고려하세요.

        다음 JSON 형식으로 결과를 반환해주세요:
        ```json
        {{
        "column_mapping": {{
            "제출양식열1": "원본데이터열A",
            "제출양식열2": "원본데이터열B"
        }},
        "explanation": "매핑에 대한 상세 설명과 근거"
        }}
        ```
        
        매핑이 불가능한 경우, column_mapping에서 해당 열을 제외하고 explanation에 이유를 설명해주세요.
        """
        
        # API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        
        # 응답 처리
        content = response.choices[0].message.content
        
        # JSON 추출 시도
        try:
            # 코드 블록에서 JSON 추출
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # 코드 블록이 없는 경우 전체 텍스트를 JSON으로 파싱 시도
            return json.loads(content)
            
        except Exception as e:
            st.error(f"JSON 파싱 오류: {str(e)}")
            st.write("AI 응답:", content)
            return None
        
    except Exception as e:
        st.error(f"OpenAI API 오류: {str(e)}")
        return None

# Gemini를 사용한 데이터 분석 및 매핑
def analyze_with_gemini(source_df, template_df, temperature=0.3):
    """Google Gemini를 사용하여 데이터 분석 및 매핑"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 데이터프레임 복사
        source_df_copy = source_df.copy()
        template_df_copy = template_df.copy()
        
        # 데이터프레임 정보 준비 (날짜/시간 객체 등 JSON 직렬화 문제 해결)
        source_cols = source_df_copy.columns.tolist()
        
        # JSON 직렬화를 위해 사용자 정의 인코더 사용
        source_sample_dict = source_df_copy.head(3).to_dict(orient='records')
        source_sample = json.loads(json.dumps(source_sample_dict, cls=CustomJSONEncoder, ensure_ascii=False))
        
        template_cols = template_df_copy.columns.tolist()
        template_sample_dict = template_df_copy.head(1).to_dict(orient='records') if not template_df_copy.empty else {}
        template_sample = json.loads(json.dumps(template_sample_dict, cls=CustomJSONEncoder, ensure_ascii=False))
        
        # 프롬프트 생성
        prompt = f"""
        당신은 데이터 분석 전문가입니다. 원본 데이터와 제출 양식을 분석하여 최적의 열 매핑을 제안해야 합니다.
        
        # 작업: 원본 데이터를 제출 양식에 맞게 매핑하기
        
        ## 원본 데이터 정보:
        - 열 목록: {source_cols}
        - 샘플 데이터: {json.dumps(source_sample, ensure_ascii=False, indent=2)}
        
        ## 제출 양식 정보:
        - 필수 열 목록: {template_cols}
        - 양식 샘플: {json.dumps(template_sample, ensure_ascii=False, indent=2)}
        
        ## 요청사항:
        1. 원본 데이터의 어떤 열이 제출 양식의 어떤 열에 매핑되어야 하는지 결정하세요.
        2. 일부 열은 직접적인 매핑이 없을 수 있으며 이 경우 적절한 기본값이나 변환 방법을 제안하세요.
        3. 데이터 타입과 형식을 고려하세요.
        
        다음 JSON 형식으로만 결과를 반환해주세요:
        {{
          "column_mapping": {{
            "제출양식열1": "원본데이터열A",
            "제출양식열2": "원본데이터열B",
            ...
          }},
          "explanation": "매핑에 대한 상세 설명과 근거"
        }}
        
        매핑이 불가능한 경우, column_mapping에서 해당 열을 제외하고 explanation에 이유를 설명해주세요.
        유효한 JSON 형식만 응답하세요. 다른 설명을 추가하지 마세요.
        """
        
        # API 호출
        model = genai.GenerativeModel("gemini-2.0-flash-lite", 
                                   generation_config={"temperature": temperature})
        response = model.generate_content(prompt)
        
        # 응답 처리
        content = response.text
        
        # JSON 추출 시도
        try:
            # 코드 블록에서 JSON 추출
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # 코드 블록이 없는 경우 전체 텍스트를 JSON으로 파싱 시도
            return json.loads(content)
            
        except Exception as e:
            st.error(f"JSON 파싱 오류: {str(e)}")
            st.write("AI 응답:", content)
            return None
        
    except Exception as e:
        st.error(f"Gemini API 오류: {str(e)}")
        return None

# 매핑에 따라 새 데이터프레임 생성
def create_mapped_dataframe(source_df, template_df, column_mapping, handle_missing="공백으로 남김"):
    """열 매핑에 따라 새 데이터프레임 생성"""
    # 결과 데이터프레임 초기화 (템플릿 열 구조 사용)
    result_df = pd.DataFrame(columns=template_df.columns)
    
    # 소스 데이터프레임의 데이터 복사
    for template_col, source_col in column_mapping.items():
        if source_col in source_df.columns:
            result_df[template_col] = source_df[source_col].copy()
    
    # 누락된 열 처리
    for col in result_df.columns:
        if col not in column_mapping or pd.isna(result_df[col]).all():
            if handle_missing == "기본값 사용":
                # 템플릿에서 기본값 추출 (첫 번째 행 사용)
                if not template_df.empty and col in template_df.columns:
                    default_value = template_df[col].iloc[0] if not pd.isna(template_df[col].iloc[0]) else ""
                    result_df[col] = default_value
            elif handle_missing == "유사 데이터로 예측":
                # 간단한 예측 로직 (실제로는 더 복잡한 알고리즘 필요)
                result_df[col] = "예측된 값"
            else:
                # 공백으로 남김
                result_df[col] = ""
    
    return result_df

# 데이터프레임 유효성 검사
def validate_dataframe(df, template_df):
    """데이터프레임 유효성 검사 및 형식 일치 확인"""
    result_df = df.copy()
    
    # 각 열의 데이터 유형 확인 및 변환
    for col in result_df.columns:
        if col in template_df.columns:
            template_dtype = template_df[col].dtype
            
            # 숫자형 데이터 처리
            if pd.api.types.is_numeric_dtype(template_dtype):
                try:
                    result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
                except:
                    pass
            
            # 날짜형 데이터 처리
            elif template_dtype == 'datetime64[ns]':
                try:
                    result_df[col] = pd.to_datetime(result_df[col], errors='coerce')
                except:
                    pass
    
    # NaN 값 처리 (빈 문자열로)
    result_df = result_df.fillna('')
    
    return result_df

# 모듈이 직접 실행될 때만 page_config 설정
if __name__ == "__main__":
    st.set_page_config(
        page_title="AI 기반 엑셀 정리하기",
        page_icon="📊",
        layout="wide"
    )
    run()