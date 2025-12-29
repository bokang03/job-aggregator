try:
    import streamlit as st
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

st.set_page_config(page_title="IT 인턴 채용공고", page_icon="💼", layout="wide")

API_URL = "http://localhost:8000"

st.title("💼 IT 인턴 채용공고 모아보기")
st.markdown("**사람인, 잡코리아, LinkedIn**의 IT 인턴 채용공고를 한 곳에서!")

with st.sidebar:
    st.header("🔍 검색 필터")

    # 플랫폼 필터
    platform = st.selectbox(
        "📌 플랫폼",
        ["전체", "사람인", "잡코리아", "LinkedIn"]
    )

    # 인턴 유형 필터
    intern_type = st.selectbox(
        "📋 인턴 유형",
        ["전체", "채용연계형", "체험형", "단기인턴", "장기인턴", "일반인턴"]
    )

    # 표시 개수
    limit = st.slider("표시 개수", 10, 200, 50)

    st.divider()

    if st.button("🔄 새 공고 크롤링", use_container_width=True):
        with st.spinner("크롤링 중... (2-3분 소요)"):
            try:
                response = requests.post(f"{API_URL}/api/crawl", timeout=300)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ 크롤링 완료! {result.get('new_jobs_added', 0)}개 추가")
                    st.rerun()
            except:
                st.error("⚠️ 서버 연결 실패")

try:
    # 통계 조회
    stats_response = requests.get(f"{API_URL}/api/stats", timeout=10)
    stats = stats_response.json() if stats_response.status_code == 200 else {}

    # 채용공고 조회
    params = {"limit": limit}
    if platform != "전체":
        params["platform"] = platform
    if intern_type != "전체":
        params["intern_type"] = intern_type

    response = requests.get(f"{API_URL}/api/jobs", params=params, timeout=10)
    jobs = response.json().get("jobs", [])

    # 통계 표시
    st.subheader("📊 플랫폼별 현황")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체", stats.get("total_jobs", 0))
    col2.metric("🟢 사람인", stats.get("by_platform", {}).get("사람인", 0))
    col3.metric("🔵 잡코리아", stats.get("by_platform", {}).get("잡코리아", 0))
    col4.metric("🟣 LinkedIn", stats.get("by_platform", {}).get("LinkedIn", 0))

    st.subheader("📋 인턴 유형별 현황")
    intern_stats = stats.get("by_intern_type", {})
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("채용연계형", intern_stats.get("채용연계형", 0))
    col2.metric("체험형", intern_stats.get("체험형", 0))
    col3.metric("단기인턴", intern_stats.get("단기인턴", 0))
    col4.metric("장기인턴", intern_stats.get("장기인턴", 0))
    col5.metric("일반인턴", intern_stats.get("일반인턴", 0))

    st.divider()

    # 현재 필터 표시
    filter_text = []
    if platform != "전체":
        filter_text.append(f"플랫폼: {platform}")
    if intern_type != "전체":
        filter_text.append(f"인턴유형: {intern_type}")

    if filter_text:
        st.info(f"🔍 필터: {', '.join(filter_text)} | 검색결과: {len(jobs)}개")
    else:
        st.info(f"📋 전체 검색결과: {len(jobs)}개")

    # 채용공고 목록
    for job in jobs:
        with st.container():
            col_main, col_side = st.columns([5, 1])

            with col_main:
                st.markdown(f"### [{job['title']}]({job['url']})")
                st.markdown(f"🏢 **{job['company']}**")

                info_parts = []
                if job.get('location'):
                    info_parts.append(f"📍 {job['location']}")
                if job.get('intern_type'):
                    info_parts.append(f"📋 {job['intern_type']}")
                if job.get('deadline'):
                    info_parts.append(f"⏰ ~{job['deadline']}")

                if info_parts:
                    st.markdown(" | ".join(info_parts))

            with col_side:
                platform_emoji = {"사람인": "🟢", "잡코리아": "🔵", "LinkedIn": "🟣"}
                st.markdown(f"### {platform_emoji.get(job['platform'], '⚪')}")
                st.caption(job['platform'])

            st.divider()

except requests.exceptions.ConnectionError:
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.info("터미널에서 `uvicorn backend.main:app --reload` 실행하세요.")
except Exception as e:
    st.error(f"❌ 오류: {e}")
