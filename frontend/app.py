import streamlit as st
import requests

st.set_page_config(page_title="백엔드 채용공고", page_icon="💼", layout="wide")

API_URL = "http://localhost:8000"

st.title("💼 백엔드 개발자 채용공고 모아보기")
st.markdown("**사람인, 잡코리아, LinkedIn** 채용공고를 한 곳에서!")

with st.sidebar:
    st.header("🔍 필터")
    platform = st.selectbox("플랫폼", ["전체", "사람인", "잡코리아", "LinkedIn"])
    limit = st.slider("표시 개수", 10, 200, 50)

    if st.button("🔄 새 공고 크롤링", use_container_width=True):
        with st.spinner("크롤링 중... (1-2분 소요)"):
            try:
                response = requests.post(f"{API_URL}/api/crawl", timeout=180)
                if response.status_code == 200:
                    st.success("✅ 크롤링 완료!")
                    st.rerun()
            except:
                st.error("⚠️ 서버 연결 실패")

try:
    params = {"limit": limit}
    if platform != "전체":
        params["platform"] = platform

    response = requests.get(f"{API_URL}/api/jobs", params=params, timeout=10)
    jobs = response.json().get("jobs", [])

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 사람인", len([j for j in jobs if j["platform"] == "사람인"]))
    col2.metric("🔵 잡코리아", len([j for j in jobs if j["platform"] == "잡코리아"]))
    col3.metric("🟣 LinkedIn", len([j for j in jobs if j["platform"] == "LinkedIn"]))

    st.divider()

    for job in jobs:
        with st.container():
            st.markdown(f"### [{job['title']}]({job['url']})")
            st.markdown(f"🏢 **{job['company']}** | 📍 {job.get('location', '-')}")
            st.divider()

except:
    st.error("⚠️ API 서버에 연결할 수 없습니다.")
    st.info("터미널에서 `uvicorn backend.main:app --reload` 실행하세요.")
