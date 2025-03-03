import streamlit as st
from PIL import Image
import base64
from io import BytesIO

def run():
    # 이전 코드는 그대로...
    
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
        st.caption("© 2025 남양주시 RPA 프로그램")

    # 페이지 헤더 수정 - 타이틀과 이모지 변경, 폰트 크기 조정
    st.markdown("""
    <style>
    .waste-title {
        font-size: 30px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        margin-bottom: 1rem;
        text-align: left;
    }    
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="waste-title">♻️ 남양주 폐기물스티커 판매정산 RPA</p>', unsafe_allow_html=True)
    st.caption("지자체 폐기물 스티커 판매 및 정산을 위한 편리한 데스크톱 애플리케이션")
    
    # 나머지 코드는 그대로...

    # 헤더 이미지 (실제 이미지가 있다면 사용, 없으면 아래 코드 제거)
    header_image = Image.open('h001.png')
    st.image(header_image, use_container_width=True)

    # 주요 기능과 작동방법을 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(["프로그램 소개", "주요 기능", "사용 방법", "다운로드"])

    # 탭 1: 프로그램 소개
    with tab1:
        st.header("프로그램 소개")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **폐기물 스티커 판매 정산 프로그램**은 남양주 읍면동에서 판매하는 폐기물 스티커의 판매 및 정산 업무를 효율적으로 관리하기 위해 개발된 프로그램입니다.
            
            이 프로그램은 다음과 같은 특징을 가지고 있습니다:
            
            - **사용자 친화적 인터페이스**: 직관적인 GUI로 누구나 쉽게 사용할 수 있습니다.
            - **스티커 데이터 관리**: 엑셀 파일을 통해 스티커 정보(분류, 품목, 규격, 가격)를 관리합니다.
            - **판매 내역 관리**: 판매 항목을 추가, 삭제, 조회할 수 있습니다.
            - **총괄 내역 생성**: 품목별 판매 실적과 총 판매액을 자동 계산합니다.
            - **엑셀 저장 기능**: 판매 내역과 총괄 내역을 엑셀 파일로 저장합니다.
            
            이 프로그램을 통해 폐기물 스티커 판매 업무를 더 빠르고 정확하게 처리할 수 있습니다.
            """)
        
        with col2:
            # 프로그램 아이콘 또는 대표 이미지
            st.markdown("### 프로그램 화면")
            
            # 실제 이미지 로드 및 그림자 효과 적용
            try:
                # 이미지를 바이트로 변환
                sample_img = Image.open('h004.png')
                buffered = BytesIO()
                sample_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # HTML/CSS로 그림자 효과 적용
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19); 
                                display: inline-block; 
                                border-radius: 5px; 
                                overflow: hidden;
                                width: 100%;">
                        <img src="data:image/png;base64,{img_str}" style="width: 100%;">
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"이미지 로드 실패 (h004.png): {e}")
            
            st.caption("프로그램 실행 화면 예시")

    # 탭 2: 주요 기능
    with tab2:
        st.header("주요 기능")
        
        features = [
            {
                "title": "스티커 가격표 불러오기",
                "description": "엑셀 파일에서 분류, 품목, 규격, 가격 정보를 불러올 수 있습니다.",
                "icon": "📊"
            },
            {
                "title": "판매 항목 관리",
                "description": "스티커 선택 후 수량을 입력하여 판매 내역에 추가하고, 항목을 개별 또는 전체 삭제할 수 있습니다.",
                "icon": "🛒"
            },
            {
                "title": "자동 계산 기능",
                "description": "수량 입력 시 자동으로 합계 금액을 계산하며, 판매 내역 추가 시 품목별 총괄 내역도 자동 업데이트됩니다.",
                "icon": "🧮"
            },
            {
                "title": "판매 실적 저장",
                "description": "판매 내역과 총괄 내역을 각각의 시트에 저장하여 체계적으로 관리할 수 있습니다.",
                "icon": "💾"
            }
        ]
        
        # 2x2 그리드로 기능 표시
        col1, col2 = st.columns(2)
        
        for i, feature in enumerate(features):
            if i % 2 == 0:
                with col1:
                    st.markdown(f"### {feature['icon']} {feature['title']}")
                    st.markdown(feature['description'])
                    st.markdown("---")
            else:
                with col2:
                    st.markdown(f"### {feature['icon']} {feature['title']}")
                    st.markdown(feature['description'])
                    st.markdown("---")
        
        # 기능 설명 이미지 (2개 행으로 배치) - 더미 이미지 대신 실제 이미지 사용
        st.subheader("주요 기능 화면")
        
        feature_cols = st.columns(2)
        with feature_cols[0]:
            try:
                img1 = Image.open('h002.png')  # 더미 이미지 대신 h002.png 사용
                st.image(img1, caption="판매내역 엑셀저장", use_container_width=True)
            except Exception as e:
                st.error(f"이미지 로드 실패 (h002.png): {e}")

        with feature_cols[1]:
            try:
                img2 = Image.open('h003.png')  # 더미 이미지 대신 h003.png 사용
                st.image(img2, caption="총괄 내역 및 저장 기능", use_container_width=True)
            except Exception as e:
                st.error(f"이미지 로드 실패 (h003.png): {e}")

    # 탭 3: 사용 방법
    with tab3:
        st.header("사용 방법")
        
        st.markdown("""
        ### 1. 프로그램 설치 및 실행
        
        1. 제공된 설치 파일을 다운로드합니다.
        2. 설치 파일을 실행하여 프로그램을 설치합니다.
        3. 바탕화면이나 시작 메뉴에서 '폐기물 스티커 판매 정산 프로그램'을 실행합니다.
        
        ### 2. 스티커 가격표 불러오기
        
        1. 프로그램 상단의 '불러오기' 버튼을 클릭합니다.
        2. 스티커 가격표 엑셀 파일을 선택합니다.
        3. 파일 형식은 Sheet1 시트에 분류, 품목, 규격, 가격 열이 포함된 엑셀 파일이어야 합니다.
        
        ### 3. 스티커 판매 등록
        
        1. 좌측의 '스티커 선택' 영역에서 분류, 품목, 규격을 순서대로 선택합니다.
        2. 선택한 스티커의 단가가 자동으로 표시됩니다.
        3. 수량을 입력하면 합계 금액이 자동 계산됩니다.
        4. '판매 추가' 버튼을 클릭하여 판매 내역에 추가합니다.
        
        ### 4. 판매 내역 관리
        
        1. 잘못 등록한 항목은 항목을 선택한 후 '선택 항목 삭제' 버튼으로 삭제할 수 있습니다.
        2. 모든 항목을 삭제하려면 '전체 삭제' 버튼을 사용합니다.
        3. 판매 내역이 추가되면 우측 하단의 총괄 내역이 자동으로 업데이트됩니다.
        
        ### 5. 판매 실적 저장
        
        1. 하단의 '찾아보기' 버튼을 클릭하여 판매 실적을 저장할 엑셀 파일을 선택합니다.
        2. '판매 내역 저장' 버튼을 클릭하면 판매 내역과 총괄 내역이 각각 다른 시트에 저장됩니다.
        3. 저장된 파일을 열어 판매 실적을 확인할 수 있습니다.
        """)
        
        # 사용 방법 시각화
        st.subheader("사용 흐름도")
        
        flow_cols = st.columns(5)
        
        steps = [
            {"title": "1. 가격표 불러오기", "icon": "📋"},
            {"title": "2. 스티커 선택", "icon": "👆"},
            {"title": "3. 수량 입력", "icon": "🔢"},
            {"title": "4. 판매 추가", "icon": "➕"},
            {"title": "5. 판매 내역 저장", "icon": "💾"}
        ]
        
        for i, col in enumerate(flow_cols):
            with col:
                st.markdown(f"### {steps[i]['icon']}")
                st.markdown(f"**{steps[i]['title']}**")

    # 탭 4: 다운로드
    with tab4:
        st.header("프로그램 다운로드")
        
        st.markdown("""
        ### 시스템 요구사항
        
        - **운영체제**: Windows 10 이상
        - **필요 프로그램**: Microsoft Excel 2009 이상
        - **필요 공간**: 50MB 이상의 여유 공간
        - **메모리**: 2GB 이상 권장
        
        ### 다운로드 방법
        
        아래 버튼을 클릭하여 프로그램 설치 파일을 다운로드하세요.
        """)
        
        # 다운로드 버튼 (실제 파일이 있을 경우 사용)
        # 임시 예시 (실제로는 파일 경로 또는 다운로드 링크를 제공)
        with st.container():
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.info("현재 다운로드는 준비 중입니다. 곧 이용 가능해질 예정입니다.")
                st.button("프로그램 다운로드", disabled=True)
        
        st.markdown("""
        ### 문의 및 지원
        
        프로그램 사용 중 문제가 발생하거나 추가 문의사항이 있으면 아래 연락처로 문의해주세요.
        
        - **이메일**: hoho4348@korea.kr
        - **전화**: 031-590-2428
        """)

    # 페이지 푸터
    st.divider()
    st.caption("© 2025 폐기물 스티커 판매 정산 프로그램 | 모든 권리 보유")

# 아래 코드는 직접 실행할 때만 작동하도록 제거 (main.py에서 호출하므로 필요 없음)
# if __name__ == "__main__":
#     main()