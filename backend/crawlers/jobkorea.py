from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import urllib.parse


class JobKoreaCrawler:
    def __init__(self):
        self.base_url = "https://www.jobkorea.co.kr/Search/?stext={}&tabType=recruit"

    def _get_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _detect_intern_type(self, title):
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

    def fetch_it_intern_jobs(self, max_jobs=50):
        driver = None
        all_jobs = []

        keywords = [
            "IT 인턴",
            "개발 인턴",
            "SW 인턴",
            "데이터 인턴"
        ]

        try:
            print("🔄 잡코리아 크롤링 시작...")
            driver = self._get_driver()

            for keyword in keywords:
                encoded_keyword = urllib.parse.quote(keyword)
                url = self.base_url.format(encoded_keyword)
                driver.get(url)
                time.sleep(2)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_items = soup.select("article.list-item")[:max_jobs]

                if not job_items:
                    job_items = soup.select("li.list-post")[:max_jobs]

                for idx, item in enumerate(job_items):
                    try:
                        title_elem = item.select_one("a.information-title-link")
                        if not title_elem:
                            title_elem = item.select_one("a.title")

                        company_elem = item.select_one("a.company-name-link")
                        if not company_elem:
                            company_elem = item.select_one("a.name")

                        if not title_elem or not company_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)

                        if "인턴" not in title.lower() and "intern" not in title.lower():
                            continue

                        href = title_elem.get('href', '')
                        if not href.startswith('http'):
                            job_url = "https://www.jobkorea.co.kr" + href
                        else:
                            job_url = href

                        intern_type = self._detect_intern_type(title)

                        all_jobs.append({
                            "job_id": "jobkorea_" + str(idx) + "_" + str(int(time.time())),
                            "title": title,
                            "company": company,
                            "url": job_url,
                            "platform": "잡코리아",
                            "location": "",
                            "experience": "인턴",
                            "education": "",
                            "salary": "",
                            "deadline": "",
                            "job_type": "IT",
                            "intern_type": intern_type
                        })

                    except Exception:
                        continue

            # 중복 제거
            seen = set()
            unique_jobs = []
            for job in all_jobs:
                key = job['company'] + "_" + job['title']
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)

            print("✅ 잡코리아에서 " + str(len(unique_jobs)) + "개 IT 인턴 공고 수집 완료")
            return unique_jobs

        except Exception as e:
            print("❌ 잡코리아 크롤링 오류: " + str(e))
            return []
        finally:
            if driver:
                driver.quit()
