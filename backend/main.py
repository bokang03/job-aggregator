from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, save_job, get_all_jobs, get_job_count_by_platform
from backend.crawlers.saramin import SaraminCrawler
from backend.crawlers.jobkorea import JobKoreaCrawler
from backend.crawlers.linkedin import LinkedInCrawler

scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def crawl_all_jobs():
    print("\n" + "=" * 50)
    print("🔄 채용공고 크롤링 시작...")
    print("=" * 50)

    new_jobs_count = 0

    try:
        saramin = SaraminCrawler()
        for job in saramin.fetch_backend_jobs(count=50):
            if save_job(job):
                new_jobs_count += 1
    except Exception as e:
        print(f"❌ 사람인 크롤링 실패: {e}")

    try:
        jobkorea = JobKoreaCrawler()
        for job in jobkorea.fetch_backend_jobs(max_jobs=30):
            if save_job(job):
                new_jobs_count += 1
    except Exception as e:
        print(f"❌ 잡코리아 크롤링 실패: {e}")

    try:
        linkedin = LinkedInCrawler()
        for job in linkedin.fetch_backend_jobs(max_jobs=20):
            if save_job(job):
                new_jobs_count += 1
    except Exception as e:
        print(f"❌ LinkedIn 크롤링 실패: {e}")

    print(f"✅ 크롤링 완료! 새로운 공고 {new_jobs_count}개 추가됨")
    return new_jobs_count


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 서버 시작 중...")
    init_db()
    crawl_all_jobs()
    scheduler.add_job(crawl_all_jobs, 'interval', hours=1, id='crawl_job')
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="백엔드 채용공고 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "백엔드 채용공고 API 서버입니다."}


@app.get("/api/jobs")
def list_jobs(platform: str = Query(None), limit: int = Query(100)):
    jobs = get_all_jobs(platform=platform, limit=limit)
    return {"total": len(jobs), "jobs": jobs}


@app.post("/api/crawl")
def trigger_crawl():
    new_count = crawl_all_jobs()
    return {"message": "크롤링 완료", "new_jobs_added": new_count}


@app.get("/api/stats")
def get_stats():
    platform_counts = get_job_count_by_platform()
    total = sum(platform_counts.values())
    return {"total_jobs": total, "by_platform": platform_counts}
