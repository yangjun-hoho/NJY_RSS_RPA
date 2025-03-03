import streamlit as st
import pandas as pd
from datetime import datetime
import os

def run():
    # 방명록 스타일 설정
    st.markdown("""
    <style>
    .guestbook-title {
        font-size: 28px !important;
        font-weight: bold;
        font-family: 'Pretendard', sans-serif;
        margin-bottom: 1rem;
        color: #4A88E5;
    }
    .guestbook-entry {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #4A88E5;
    }
    .guestbook-date {
        color: #6c757d;
        font-size: 14px;
        text-align: right;
        margin-top: 8px;
    }
    .guestbook-message {
        white-space: pre-line;
    }
    .admin-section {
        margin-top: 30px;
        padding: 15px;
        border: 1px dashed #ddd;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 방명록 헤더
    st.markdown("이 방명록은 남양주시 AI & RPA 연구 관련 의견이나 피드백을 남기는 공간입니다.")
    
    # 방명록 데이터 파일 경로
    GUESTBOOK_FILE = "guestbook_data.csv"
    
    # 방명록 데이터 로드
    if os.path.exists(GUESTBOOK_FILE):
        guestbook_df = pd.read_csv(GUESTBOOK_FILE)
    else:
        guestbook_df = pd.DataFrame(columns=["message", "timestamp"])
    
    # 방명록 작성 영역
    st.subheader("📝의견 남기기")
    
    message = st.text_area("메시지", height=68, placeholder="의견이나 피드백을 남겨주세요.")
    
    if st.button("작성하기"):
        if message:
            # 현재 시간
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 새 방명록 항목 추가
            new_entry = {
                "message": str(message),  # 문자열로 저장 보장
                "timestamp": current_time
            }
            
            # 데이터프레임에 추가
            guestbook_df = pd.concat([pd.DataFrame([new_entry]), guestbook_df], ignore_index=True)
            
            # CSV 파일로 저장
            guestbook_df.to_csv(GUESTBOOK_FILE, index=False)
            
            st.success("방명록이 작성되었습니다!")
            
            # 페이지 새로고침 (입력창 초기화) - experimental_rerun을 rerun으로 변경
            st.rerun()
    
    # 구분선
    st.divider()
    
    # 방명록 목록 표시
    st.subheader("방명록 목록")
    
    if guestbook_df.empty:
        st.info("아직 작성된 방명록이 없습니다. 첫 번째 방명록을 작성해 보세요!")
    else:
        # 최신 항목부터 표시
        for index, entry in guestbook_df.iterrows():
            # 메시지가 문자열이 아닌 경우 문자열로 변환
            message_str = str(entry['message']) if entry['message'] is not None else ""
            timestamp_str = str(entry['timestamp']) if entry['timestamp'] is not None else ""
            
            st.markdown(f"""
            <div class="guestbook-entry">
                <div class="guestbook-message">{message_str}</div>
                <div class="guestbook-date">{timestamp_str}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 하단 구분선
    st.divider()
    st.caption("방명록은 지속적으로 모니터링되고 있으며, 부적절한 내용은 관리자에 의해 삭제될 수 있습니다.")
    
    # 관리자 섹션 (확장 가능한 영역으로 숨김)
    with st.expander("관리자 기능"):
        st.markdown('<div class="admin-section">', unsafe_allow_html=True)
        st.subheader("방명록 관리")
        
        admin_password = st.text_input("관리자 비밀번호", type="password")
        ADMIN_PASSWORD = "203843"  # 실제 사용 시 더 강력한 비밀번호로 변경하세요
        
        if admin_password == ADMIN_PASSWORD:
            st.success("관리자 인증 성공")
            
            if not guestbook_df.empty:
                # 방명록 선택 및 삭제 기능
                st.write("삭제할 방명록을 선택하세요:")
                
                # 각 방명록 항목에 대한 선택 위젯 생성
                delete_options = []
                for index, entry in guestbook_df.iterrows():
                    # 메시지와 시간을 문자열로 변환하여 사용
                    message_str = str(entry['message']) if entry['message'] is not None else ""
                    timestamp_str = str(entry['timestamp']) if entry['timestamp'] is not None else ""
                    
                    # 메시지 일부와 시간을 포함한 식별자 생성 (메시지가 문자열임을 보장)
                    if len(message_str) > 30:
                        msg_preview = message_str[:30] + "..."
                    else:
                        msg_preview = message_str
                        
                    option_text = f"{msg_preview} ({timestamp_str})"
                    delete_options.append((option_text, index))
                
                # 목록에서 선택
                selected_indices = []
                for text, idx in delete_options:
                    if st.checkbox(text, key=f"delete_{idx}"):
                        selected_indices.append(idx)
                
                if selected_indices and st.button("선택한 방명록 삭제"):
                    # 선택된 인덱스의 방명록 삭제
                    guestbook_df = guestbook_df.drop(selected_indices).reset_index(drop=True)
                    guestbook_df.to_csv(GUESTBOOK_FILE, index=False)
                    st.success(f"{len(selected_indices)}개의 방명록이 삭제되었습니다.")
                    st.rerun()  # experimental_rerun을 rerun으로 변경
                
                # 전체 삭제 옵션
                if st.button("모든 방명록 삭제", help="모든 방명록을 삭제합니다. 이 작업은 되돌릴 수 없습니다."):
                    # 확인 대화상자
                    confirm = st.checkbox("정말로 모든 방명록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
                    if confirm and st.button("예, 모두 삭제합니다"):
                        # 방명록 전체 삭제
                        guestbook_df = pd.DataFrame(columns=["message", "timestamp"])
                        guestbook_df.to_csv(GUESTBOOK_FILE, index=False)
                        st.success("모든 방명록이 삭제되었습니다.")
                        st.rerun()  # experimental_rerun을 rerun으로 변경
            else:
                st.info("삭제할 방명록이 없습니다.")
                
        elif admin_password and admin_password != ADMIN_PASSWORD:
            st.error("비밀번호가 일치하지 않습니다.")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()
