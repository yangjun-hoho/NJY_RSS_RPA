import streamlit as st
import os
import base64
import tempfile
import asyncio
import subprocess
from io import BytesIO
from gtts import gTTS
from PIL import Image
import time

# python-docx 패키지 체크
try:
    from docx import Document
    docx_available = True
except ImportError:
    docx_available = False

# PyPDF2 패키지 체크
try:
    import PyPDF2
    pdf_available = True
except ImportError:
    pdf_available = False

# edge-tts 패키지 체크
try:
    import edge_tts
    edge_tts_available = True
except ImportError:
    edge_tts_available = False

def run():
    # 사이드바 설정
    with st.sidebar:
        st.divider()
        # AI 모델 선택
        model_provider = st.radio(
            "🤖 TTS 모델 선택",
            ["Microsoft Edge TTS", "Google TTS"]
        )
        
        if model_provider == "Microsoft Edge TTS" and not edge_tts_available:
            st.warning("Microsoft Edge TTS를 사용하려면 `pip install edge-tts` 명령어로 패키지를 설치해주세요.")
        
        # 음성 설정
        st.markdown("### 음성 설정")
        
        # 언어 및 음성 선택
        language = st.selectbox(
            "언어 선택",
            ["한국어", "영어", "일본어", "중국어", "프랑스어"],
            index=0
        )
        
        # 언어에 따른 코드 맵핑
        lang_code = {
            "한국어": "ko",
            "영어": "en",
            "일본어": "ja",
            "중국어": "zh-CN",
            "프랑스어": "fr"
        }
        
        # Edge TTS용 음성 선택
        voice_name = None
        if model_provider == "Microsoft Edge TTS" and edge_tts_available:
            # 언어별 Edge TTS 음성 목록
            edge_voices = {
                "한국어": ["ko-KR-SunHiNeural (여성)", "ko-KR-InJoonNeural (남성)",],
                "영어": ["en-US-AriaNeural (여성)", "en-US-GuyNeural (남성)", "en-GB-SoniaNeural (여성)"],
                "일본어": ["ja-JP-NanamiNeural (여성)", "ja-JP-KeitaNeural (남성)"],
                "중국어": ["zh-CN-XiaoxiaoNeural (여성)", "zh-CN-YunjianNeural (남성)"],
                "프랑스어": ["fr-FR-DeniseNeural (여성)", "fr-FR-HenriNeural (남성)"]
            }
            
            voice_options = edge_voices.get(language, ["기본 음성"])
            selected_voice = st.selectbox("음성 선택", voice_options)
            
            # 음성 이름 추출 (괄호 앞 부분)
            voice_name = selected_voice.split(" (")[0] if " (" in selected_voice else selected_voice
        
        # 음성 속도 조절
        speed = st.slider("🔊 음성 속도", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        
        st.divider()
        st.caption("© 2025 남양주시 AI TTS 변환기")

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
    /* 텍스트 영역 상단 여백 조정 */
    .stTextArea {
        margin-top: 0rem !important;
        margin-bottom: 2rem !important;        
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
    .text-preview {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        max-height: 300px;
        overflow-y: auto;
        font-family: 'Pretendard', sans-serif;
    }
    .audio-box {
        background-color: #eef7ed;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        border-left: 4px solid #167331;
    }
    </style>
    """, unsafe_allow_html=True)

    # 헤더 및 설명 (두 번째 코드 방식으로 변경)
    st.title("🔊 AI TTS 음성 변환기")
    st.caption("텍스트를 자연스러운 음성으로 변환하여 들어보세요. 파일 업로드 또는 직접 입력이 가능합니다.")

    # 세션 상태 초기화
    if "tts_text" not in st.session_state:
        st.session_state.tts_text = ""
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
    if "last_model" not in st.session_state:
        st.session_state.last_model = None
    if "last_voice" not in st.session_state:
        st.session_state.last_voice = None
    if "last_text" not in st.session_state:
        st.session_state.last_text = None
    if "last_speed" not in st.session_state:
        st.session_state.last_speed = None
    if "last_language" not in st.session_state:
        st.session_state.last_language = None
    
    # Google TTS로 음성 생성하는 함수
    def generate_google_tts(text, language, speed):
        try:
            tts = gTTS(text=text, lang=lang_code[language], slow=(speed < 0.9))
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            return audio_bytes.read()
        except Exception as e:
            raise Exception(f"Google TTS 오류: {str(e)}")
    
    # Edge TTS로 음성 생성하는 함수 (명령줄 직접 실행 방식)
    def generate_edge_tts_cmd(text, voice_name, speed):
        try:
            # 임시 파일 생성
            text_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
            text_file.write(text)
            text_file.close()
            
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_file.close()
            
            # 속도 값 계산
            speed_percent = int((speed - 1.0) * 100)
            rate_option = f"--rate={speed_percent:+d}%" if speed != 1.0 else ""
            
            # edge-tts 명령줄 도구 직접 실행
            cmd = f"edge-tts --voice {voice_name} --file {text_file.name} {rate_option} --write-media {output_file.name}"
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if process.returncode != 0:
                raise Exception(f"Edge TTS 명령 실패: {process.stderr}")
            
            # 결과 파일 읽기
            with open(output_file.name, "rb") as f:
                audio_data = f.read()
            
            # 임시 파일 삭제
            os.unlink(text_file.name)
            os.unlink(output_file.name)
            
            return audio_data
        except Exception as e:
            raise Exception(f"Edge TTS 오류: {str(e)}")
    
    async def list_edge_voices():
        try:
            voices = await edge_tts.VoicesManager.create()
            return voices.voices
        except Exception as e:
            raise Exception(f"음성 목록 가져오기 실패: {str(e)}")

    # Edge TTS로 음성 생성하는 비동기 함수 (API 사용 방식)
    async def generate_edge_tts_async(text, voice_name, speed):
        try:
            # 사용 가능한 음성 목록 확인
            voices = await list_edge_voices()
            available_voices = [v["ShortName"] for v in voices]
            
            # 음성 이름 확인 및 수정
            if voice_name not in available_voices:
                # 대체 음성 찾기
                language_code = voice_name.split('-')[0]
                matching_voices = [v for v in available_voices if v.startswith(language_code)]
                
                if matching_voices:
                    voice_name = matching_voices[0]
                    st.info(f"지정한 음성을 찾을 수 없어 {voice_name}(으)로 대체합니다.")
                else:
                    # 기본 영어 음성으로 대체
                    voice_name = "en-US-AriaNeural"
                    st.warning(f"호환되는 음성을 찾을 수 없어 기본 음성({voice_name})을 사용합니다.")
            
            # 간단한 방식으로 시도
            communicate = edge_tts.Communicate(text, voice_name)
            
            # 임시 출력 파일 생성
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_file.close()
            
            # 가장 기본적인 방식으로 시도 - 추가 매개변수 없이
            await communicate.save(output_file.name)
            
            # 결과 파일 읽기
            with open(output_file.name, "rb") as f:
                audio_data = f.read()
            
            # 임시 파일 삭제
            os.unlink(output_file.name)
            
            return audio_data
        except Exception as e:
            raise Exception(f"Edge TTS 비동기 오류: {str(e)}")
    
    # Edge TTS 생성 통합 함수 (API와 명령줄 방식 모두 시도)
    def generate_edge_tts(text, voice_name, speed):
        try:
            # 먼저 API 방식 시도
            if edge_tts_available:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return loop.run_until_complete(generate_edge_tts_async(text, voice_name, speed))
                except Exception as e:
                    st.warning(f"Edge TTS API 방식 실패: {str(e)}. 명령줄 방식으로 시도합니다.")
            
            # 명령줄 방식 시도
            return generate_edge_tts_cmd(text, voice_name, speed)
            
        except Exception as e:
            # 모든 방식 실패 시
            raise Exception(f"Edge TTS 생성 실패: {str(e)}")
    
    # 입력 방식 선택 (탭 대신 라디오 버튼 사용)
    input_method = st.radio("입력 방식 선택", ["텍스트 직접 입력", "파일 업로드"])
    
    # 텍스트 직접 입력
    if input_method == "텍스트 직접 입력":
        st.markdown('<p class="sub-title">텍스트 직접 입력</p>', unsafe_allow_html=True)
        
        # 텍스트 입력 영역
        text_input = st.text_area(
            "변환할 텍스트를 입력하세요",
            value=st.session_state.tts_text,
            height=200,
            placeholder="여기에 음성으로 변환할 텍스트를 입력하세요. 길이 제한은 5000자입니다."
        )
        
        # 변환 버튼
        if st.button("🔊 음성으로 변환", type="primary", use_container_width=True):
            if text_input.strip():
                if len(text_input) > 5000:
                    st.warning("텍스트가 너무 깁니다. 5000자 이내로 입력해주세요.")
                else:
                    st.session_state.tts_text = text_input
                    
                    # 이전과 다른 설정인 경우에만 음성 다시 생성
                    settings_changed = (
                        st.session_state.last_model != model_provider or
                        st.session_state.last_text != text_input or
                        st.session_state.last_speed != speed or
                        st.session_state.last_language != language
                    )
                    
                    if model_provider == "Microsoft Edge TTS" and hasattr(st.session_state, 'last_voice'):
                        settings_changed = settings_changed or (st.session_state.last_voice != voice_name)
                    
                    if settings_changed:
                        with st.spinner("음성을 생성하고 있습니다..."):
                            try:
                                if model_provider == "Google TTS":
                                    st.session_state.audio_data = generate_google_tts(text_input, language, speed)
                                    st.session_state.last_model = "Google TTS"
                                    st.session_state.last_voice = None
                                
                                elif model_provider == "Microsoft Edge TTS" and (edge_tts_available or True):  # 명령줄 방식은 패키지 없이도 가능
                                    st.session_state.audio_data = generate_edge_tts(text_input, voice_name, speed)
                                    st.session_state.last_model = "Microsoft Edge TTS"
                                    st.session_state.last_voice = voice_name
                                
                                else:
                                    st.warning("Microsoft Edge TTS 사용 불가. Google TTS를 사용합니다.")
                                    st.session_state.audio_data = generate_google_tts(text_input, language, speed)
                                    st.session_state.last_model = "Google TTS"
                                    st.session_state.last_voice = None
                                
                                # 현재 설정 저장
                                st.session_state.last_text = text_input
                                st.session_state.last_speed = speed
                                st.session_state.last_language = language
                                
                                st.success("음성이 생성되었습니다!")
                            
                            except Exception as e:
                                st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.info("이전과 동일한 설정입니다. 이미 생성된 음성을 사용합니다.")
            else:
                st.warning("변환할 텍스트를 입력해주세요.")
    
    # 파일 업로드
    else:
        st.markdown('<p class="sub-title">파일에서 텍스트 추출</p>', unsafe_allow_html=True)
        
        # 지원 가능한 파일 형식 확인
        supported_types = ["txt"]
        if docx_available:
            supported_types.append("docx")
        if pdf_available:
            supported_types.append("pdf")
        
        uploaded_file = st.file_uploader("텍스트가 포함된 파일을 업로드하세요", 
                                        type=supported_types)
        
        extracted_text = ""
        
        if uploaded_file is not None:
            with st.spinner("파일에서 텍스트를 추출하고 있습니다..."):
                try:
                    # 파일 형식에 따른 처리
                    if uploaded_file.name.endswith('.txt'):
                        extracted_text = uploaded_file.read().decode('utf-8')
                    
                    elif uploaded_file.name.endswith('.docx') and docx_available:
                        # 임시 파일로 저장
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # docx 파일 읽기
                        doc = Document(tmp_path)
                        extracted_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                        os.unlink(tmp_path)  # 임시 파일 삭제
                    
                    elif uploaded_file.name.endswith('.pdf') and pdf_available:
                        # 임시 파일로 저장
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # PDF 파일 읽기
                        with open(tmp_path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            text_chunks = []
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                text_chunks.append(page.extract_text())
                            extracted_text = '\n'.join(text_chunks)
                        os.unlink(tmp_path)  # 임시 파일 삭제
                    
                    # 추출된 텍스트 표시
                    if extracted_text:
                        st.success("파일에서 텍스트를 성공적으로 추출했습니다!")
                        # 텍스트 미리보기 (최대 1000자)
                        st.markdown("### 추출된 텍스트 미리보기")
                        preview_text = extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else "")
                        st.markdown(f'<div class="text-preview">{preview_text}</div>', unsafe_allow_html=True)
                        
                        # 텍스트 편집 기능
                        edited_text = st.text_area("필요시 텍스트를 편집하세요", 
                                               value=extracted_text, 
                                               height=200)
                        
                        # 변환 버튼
                        if st.button("🔊 파일 내용을 음성으로 변환", type="primary", use_container_width=True):
                            if edited_text.strip():
                                if len(edited_text) > 5000:
                                    st.warning("텍스트가 너무 깁니다. 5000자 이내로 입력해주세요.")
                                else:
                                    st.session_state.tts_text = edited_text
                                    
                                    with st.spinner("음성을 생성하고 있습니다..."):
                                        try:
                                            if model_provider == "Google TTS":
                                                st.session_state.audio_data = generate_google_tts(edited_text, language, speed)
                                                st.session_state.last_model = "Google TTS"
                                                st.session_state.last_voice = None
                                            
                                            elif model_provider == "Microsoft Edge TTS" and (edge_tts_available or True):
                                                st.session_state.audio_data = generate_edge_tts(edited_text, voice_name, speed)
                                                st.session_state.last_model = "Microsoft Edge TTS"
                                                st.session_state.last_voice = voice_name
                                            
                                            else:
                                                st.warning("Microsoft Edge TTS 사용 불가. Google TTS를 사용합니다.")
                                                st.session_state.audio_data = generate_google_tts(edited_text, language, speed)
                                                st.session_state.last_model = "Google TTS"
                                                st.session_state.last_voice = None
                                            
                                            # 현재 설정 저장
                                            st.session_state.last_text = edited_text
                                            st.session_state.last_speed = speed
                                            st.session_state.last_language = language
                                            
                                            st.success("음성이 생성되었습니다!")
                                        
                                        except Exception as e:
                                            st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")
                            else:
                                st.warning("변환할 텍스트가 없습니다.")
                    else:
                        st.warning("파일에서 텍스트를 추출할 수 없습니다.")
                
                except Exception as e:
                    st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
    
    # 생성된 오디오 표시
    if st.session_state.audio_data:
        st.markdown("---")
        st.markdown('<p class="sub-title">생성된 음성</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="audio-box">', unsafe_allow_html=True)
        
        # 모델 및 설정 정보 표시
        model_info = st.session_state.last_model or "Google TTS"
        voice_info = ""
        if model_info == "Microsoft Edge TTS" and st.session_state.last_voice:
            voice_info = f" - {st.session_state.last_voice}"
            
        st.markdown(f"**사용 모델**: {model_info}{voice_info}")
        
        # 오디오 컨트롤
        st.audio(st.session_state.audio_data, format="audio/mp3")
        
        # 다운로드 버튼
        current_time = time.strftime("%Y%m%d_%H%M%S")
        model_suffix = "edge" if model_info == "Microsoft Edge TTS" else "google"
        st.download_button(
            label="🔽 음성 파일 다운로드 (MP3)",
            data=st.session_state.audio_data,
            file_name=f"tts_{model_suffix}_{current_time}.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 하단 정보 표시
    st.markdown("---")
    st.markdown("""
    ### 활용 방법
    
    - **회의 자료 음성화**: 회의 자료를 음성으로 변환하여 이동 중에도 확인 가능
    - **발표 준비**: 발표 원고를 음성으로 변환하여 톤과 흐름 확인
    - **문서 접근성 향상**: 시각장애인을 위한 문서 음성화
    - **외국어 학습**: 외국어 텍스트의 발음 확인
    """)
    
    # 패키지 설치 안내
    if not edge_tts_available:
        st.info("""
        **Microsoft Edge TTS를 사용하려면**:
        
        ```
        pip install edge-tts
        ```
        
        명령어로 패키지를 설치해주세요. Edge TTS는 더 자연스러운 음성과 다양한 목소리 옵션을 제공합니다.
        """)
    
    # 페이지 푸터
    st.caption("© 2025 남양주시 AI TTS 변환기 | 모든 권리 보유")

if __name__ == "__main__":
    run()