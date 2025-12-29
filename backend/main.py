try:
    from fastapi import FastAPI, Query
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    pass

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
    pass

from contextlib import asynccontextmanager
import sys
import os

# 현재 파일 기준으로 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# 상대 경로 import로 변경
try:
    from database import init_db, save_job, get_all_jobs, get_job_count_by_platform, get_job_count_by_intern_type
except ImportError:
    from backend.database import init_db, save_job, get_all_jobs, get_job_count_by_platform, get_job_count_by_intern_type

try:
    from crawlers.saramin import SaraminCrawler
except ImportError:
    from backend.crawlers.saramin import SaraminCrawler

try:
    from crawlers.jobkorea import JobKoreaCrawler
except ImportError:
    from backend.crawlers.jobkorea import JobKoreaCrawler

try:
    from crawlers.linkedin import LinkedInCrawler
except ImportError:
    from backend.crawlers.linkedin import LinkedInCrawler

scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def crawl_all_jobs():
    print("\n" + "=" * 50)
    print("🔄 IT 인턴 채용공고 크롤링 시작...")
    print("=" * 50)

    new_jobs_count = 0

    try:
        saramin = SaraminCrawler()
        for job in saramin.fetch_it_intern_jobs(count=50):
            if save_job(job):
                new_jobs_count += 1
    except Exception as e:
        print(f"❌ 사람인 크롤링 실패: {e}")

    try:
        jobkorea = JobKoreaCrawler()
        for job in jobkorea.fetch_it_intern_jobs(max_jobs=30):
            if save_job(job):
                new_jobs_count += 1
    except Exception as e:
        print(f"❌ 잡코리아 크롤링 실패: {e}")

    try:
        linkedin = LinkedInCrawler()
        for job in linkedin.fetch_it_intern_jobs(max_jobs=20):
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


app = FastAPI(title="IT 인턴 채용공고 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "IT 인턴 채용공고 API 서버입니다."}


@app.get("/api/jobs")
def list_jobs(
    platform: str = Query(None, description="플랫폼 (사람인, 잡코리아, LinkedIn)"),
    intern_type: str = Query(None, description="인턴 유형 (채용연계형, 체험형, 단기인턴, 장기인턴, 일반인턴)"),
    limit: int = Query(100)
):
    jobs = get_all_jobs(platform=platform, intern_type=intern_type, limit=limit)
    return {"total": len(jobs), "jobs": jobs}


@app.post("/api/crawl")
def trigger_crawl():
    new_count = crawl_all_jobs()
    return {"message": "크롤링 완료", "new_jobs_added": new_count}


@app.get("/api/stats")
def get_stats():
    platform_counts = get_job_count_by_platform()
    intern_type_counts = get_job_count_by_intern_type()
    total = sum(platform_counts.values())
    return {
        "total_jobs": total,
        "by_platform": platform_counts,
        "by_intern_type": intern_type_counts
    }
