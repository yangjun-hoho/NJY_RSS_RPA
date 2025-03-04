import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd
import sqlite3

class UsageCounter:
    """
    앱 사용량을 추적하는 카운터 클래스
    JSON 파일 기반으로 각 앱의 사용 횟수(오늘, 누적)를 관리
    """
    def __init__(self, counter_file="usage_counter.json"):
        """
        사용량 카운터 초기화
        
        Parameters:
        counter_file (str): 카운터 데이터를 저장할 JSON 파일 경로
        """
        self.counter_file = counter_file
        self.counters = self._load_counters()
    
    def _load_counters(self):
        """카운터 파일에서 데이터 로드"""
        if os.path.exists(self.counter_file):
            try:
                with open(self.counter_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except Exception as e:
                # 파일 로드 실패 시 빈 카운터 반환
                return {}
        else:
            return {}
    
    def _save_counters(self):
        """카운터 데이터를 파일에 저장"""
        try:
            with open(self.counter_file, 'w', encoding='utf-8') as file:
                json.dump(self.counters, file, ensure_ascii=False, indent=2)
        except Exception as e:
            # 저장 실패 시 콘솔에 오류 출력 (개발 모드에서 확인용)
            print(f"카운터 파일 저장 오류: {e}")
    
    def increment(self, app_name):
        """
        특정 앱의 사용 횟수 증가
        
        Parameters:
        app_name (str): 앱 이름
        
        Returns:
        dict: 현재 앱의 사용량 통계 (오늘 사용량, 총 사용량)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 해당 앱의 카운터가 없으면 초기화
        if app_name not in self.counters:
            self.counters[app_name] = {
                "total": 0,
                "daily": {}
            }
        
        # 오늘 날짜의 카운터가 없으면 초기화
        if today not in self.counters[app_name]["daily"]:
            self.counters[app_name]["daily"][today] = 0
        
        # 카운터 증가
        self.counters[app_name]["daily"][today] += 1
        self.counters[app_name]["total"] += 1
        
        # 변경사항 저장
        self._save_counters()
        
        return {
            "today": self.counters[app_name]["daily"][today],
            "total": self.counters[app_name]["total"]
        }
    
    def get_stats(self, app_name=None):
        """
        사용량 통계 조회
        
        Parameters:
        app_name (str, optional): 앱 이름. None이면 모든 앱의 통계 반환
        
        Returns:
        dict: 앱 사용량 통계
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        if app_name:
            if app_name in self.counters:
                today_count = self.counters[app_name]["daily"].get(today, 0)
                return {
                    "today": today_count,
                    "total": self.counters[app_name]["total"]
                }
            else:
                return {"today": 0, "total": 0}
        else:
            stats = {}
            for app, data in self.counters.items():
                today_count = data["daily"].get(today, 0)
                stats[app] = {
                    "today": today_count,
                    "total": data["total"]
                }
            return stats
    
    def get_all_apps_dataframe(self):
        """
        모든 앱의 통계를 데이터프레임으로 반환
        
        Returns:
        pandas.DataFrame: 앱별 사용량 통계 데이터프레임
        """
        stats = self.get_stats()
        data = []
        
        for app_name, app_stats in stats.items():
            data.append({
                "앱 이름": app_name,
                "오늘 사용횟수": app_stats["today"],
                "전체 사용횟수": app_stats["total"]
            })
        
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(columns=["앱 이름", "오늘 사용횟수", "전체 사용횟수"])
    
    def get_history_dataframe(self, app_name=None, days=30):
        """
        앱 사용 기록을 데이터프레임으로 반환
        
        Parameters:
        app_name (str, optional): 앱 이름. None이면 전체 앱의 일별 합계
        days (int): 가져올 일수
        
        Returns:
        pandas.DataFrame: 사용 기록 데이터프레임
        """
        if app_name and app_name in self.counters:
            # 특정 앱의 사용 기록
            daily_data = self.counters[app_name]["daily"]
            data = []
            
            for date, count in daily_data.items():
                data.append({
                    "날짜": date,
                    "사용횟수": count
                })
            
            if data:
                df = pd.DataFrame(data)
                df["날짜"] = pd.to_datetime(df["날짜"])
                df = df.sort_values("날짜", ascending=False).head(days)
                return df
            else:
                return pd.DataFrame(columns=["날짜", "사용횟수"])
        
        elif not app_name:
            # 모든 앱의 일별 합계
            date_counts = {}
            
            for app, data in self.counters.items():
                for date, count in data["daily"].items():
                    if date in date_counts:
                        date_counts[date] += count
                    else:
                        date_counts[date] = count
            
            data = [{"날짜": date, "사용횟수": count} for date, count in date_counts.items()]
            
            if data:
                df = pd.DataFrame(data)
                df["날짜"] = pd.to_datetime(df["날짜"])
                df = df.sort_values("날짜", ascending=False).head(days)
                return df
            else:
                return pd.DataFrame(columns=["날짜", "사용횟수"])
        
        else:
            return pd.DataFrame(columns=["날짜", "사용횟수"])

# 앱 사용량 카운트 함수
def count_app_usage(app_name):
    """
    앱 사용량 카운트 증가
    
    Parameters:
    app_name (str): 앱 이름
    
    Returns:
    dict: 현재 앱의 사용량 통계
    """
    counter = UsageCounter()
    return counter.increment(app_name)

# 현재 앱의 사용량 통계 표시
def display_current_app_stats(app_name):
    """
    현재 앱의 사용량 통계 표시
    
    Parameters:
    app_name (str): 앱 이름
    """
    counter = UsageCounter()
    stats = counter.get_stats(app_name)
    
    # 새로운 컨테이너 스타일 정의
    st.markdown("""
    <style>
    .stats-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin-top: 10px;
        margin-bottom: 15px;
        border-left: 3px solid #4A88E5;
    }
    .stats-title {
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 5px;
        color: #1E3A8A;
    }
    .stats-value {
        font-size: 20px;
        font-weight: bold;
        color: #4A88E5;
    }
    .stats-label {
        font-size: 12px;
        color: #6B7280;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 사이드바에 통계 표시
    with st.sidebar:
        st.markdown(f"""
        <div class="stats-container">
            <div class="stats-title">💾 {app_name}</div>
            <table width="100%">
                <tr>
                    <td width="50%">
                        <div class="stats-value">{stats['today']:,}</div>
                        <div class="stats-label">오늘 사용횟수</div>
                    </td>
                    <td width="50%">
                        <div class="stats-value">{stats['total']:,}</div>
                        <div class="stats-label">누적 사용횟수</div>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# 모든 앱의 사용량 통계 표시 (관리자용)
def display_all_app_stats(show_detail=False):
    """
    모든 앱의 사용량 통계 표시
    
    Parameters:
    show_detail (bool): 상세 정보 표시 여부
    """
    counter = UsageCounter()
    
    if show_detail:
        # 관리자 모드에서 모든 앱 통계 표시
        st.subheader("📊 앱 사용량 통계")
        
        # 앱별 통계
        df = counter.get_all_apps_dataframe()
        if not df.empty:
            # 데이터프레임을 총 사용량으로 정렬
            df = df.sort_values(by="전체 사용횟수", ascending=False)
            st.dataframe(df, use_container_width=True)
            
            # 가장 많이 사용된 앱 차트
            st.subheader("🔝 앱별 사용량")
            chart_data = df.set_index("앱 이름")
            st.bar_chart(chart_data)
            
            # 일별 사용량 추이
            st.subheader("📅 일별 사용량 추이")
            history_df = counter.get_history_dataframe(days=30)
            if not history_df.empty:
                history_df = history_df.sort_values("날짜")
                chart_data = history_df.set_index("날짜")
                st.line_chart(chart_data)
            else:
                st.info("사용 기록이 없습니다.")
        else:
            st.info("사용 기록이 없습니다.")
    else:
        # 간략한 통계만 표시 (사이드바 등에 사용)
        df = counter.get_all_apps_dataframe()
        if not df.empty:
            with st.expander("📊 모든 앱 사용량 통계", expanded=False):
                st.dataframe(df, use_container_width=True)

# 관리자 페이지 (선택적 사용)
def admin_stats_page():
    """관리자용 통계 페이지"""
    st.title("📊 앱 사용량 통계 대시보드")
    st.caption("모든 앱의 사용량 통계를 확인할 수 있습니다.")
    
    display_all_app_stats(show_detail=True)