import requests
import os
from dotenv import load_dotenv

load_dotenv()


class SaraminCrawler:
    def __init__(self):
        self.access_key = os.getenv('SARAMIN_API_KEY')
        self.base_url = "https://oapi.saramin.co.kr/job-search"

    def fetch_backend_jobs(self, count=50):
        if not self.access_key:
            print("❌ 사람인 API 키가 설정되지 않았습니다.")
            return []

        params = {
            "access-key": self.access_key,
            "keywords": "백엔드 개발자",
            "job_mid_cd": "22",
            "count": count,
            "sort": "pd"
        }

        headers = {"Accept": "application/json"}

        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            jobs = data.get("jobs", {}).get("job", [])
            result = []

            for job in jobs:
                company_info = job.get("company", {}).get("detail", {})
                position_info = job.get("position", {})

                result.append({
                    "job_id": f"saramin_{job.get('id')}",
                    "title": position_info.get("title", ""),
                    "company": company_info.get("name", ""),
                    "url": job.get("url", ""),
                    "platform": "사람인",
                    "location": position_info.get("location", {}).get("name", ""),
                    "experience": position_info.get("experience-level", {}).get("name", ""),
                    "education": position_info.get("required-education-level", {}).get("name", ""),
                    "salary": job.get("salary", {}).get("name", ""),
                    "deadline": job.get("expiration-date", "")
                })

            print(f"✅ 사람인에서 {len(result)}개 공고 수집 완료")
            return result

        except Exception as e:
            print(f"❌ 사람인 API 오류: {e}")
            return []
