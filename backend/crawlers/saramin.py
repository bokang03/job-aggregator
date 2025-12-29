import requests
import os
from dotenv import load_dotenv

load_dotenv()


class SaraminCrawler:
    def __init__(self):
        self.access_key = os.getenv('SARAMIN_API_KEY')
        self.base_url = "https://oapi.saramin.co.kr/job-search"

    def _detect_intern_type(self, title, experience):
        if "채용연계" in title or "정규직전환" in title or "전환형" in title:
            return "채용연계형"
        elif "체험" in title or "체험형" in title:
            return "체험형"
        elif "단기" in title:
            return "단기인턴"
        elif "장기" in title:
            return "장기인턴"
        elif "인턴" in title:
            return "일반인턴"
        else:
            return "인턴"

    def fetch_it_intern_jobs(self, count=50):
        if not self.access_key:
            print("❌ 사람인 API 키가 설정되지 않았습니다.")
            return []

        keywords_list = [
            "IT 인턴",
            "개발자 인턴",
            "SW 인턴",
            "데이터 인턴"
        ]

        all_jobs = []

        for keyword in keywords_list:
            params = {
                "access-key": self.access_key,
                "keywords": keyword,
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

                for job in jobs:
                    company_info = job.get("company", {}).get("detail", {})
                    position_info = job.get("position", {})
                    title = position_info.get("title", "")
                    experience = position_info.get("experience-level", {}).get("name", "")

                    if "인턴" not in title.lower() and "intern" not in title.lower():
                        continue

                    intern_type = self._detect_intern_type(title, experience)

                    all_jobs.append({
                        "job_id": "saramin_" + str(job.get('id')),
                        "title": title,
                        "company": company_info.get("name", ""),
                        "url": job.get("url", ""),
                        "platform": "사람인",
                        "location": position_info.get("location", {}).get("name", ""),
                        "experience": experience,
                        "education": position_info.get("required-education-level", {}).get("name", ""),
                        "salary": job.get("salary", {}).get("name", ""),
                        "deadline": job.get("expiration-date", ""),
                        "job_type": "IT",
                        "intern_type": intern_type
                    })

            except Exception as e:
                print("❌ 사람인 API 오류: " + str(e))
                continue

        # 중복 제거
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            if job['job_id'] not in seen:
                seen.add(job['job_id'])
                unique_jobs.append(job)

        print("✅ 사람인에서 " + str(len(unique_jobs)) + "개 IT 인턴 공고 수집 완료")
        return unique_jobs
