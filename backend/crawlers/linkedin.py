from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


class LinkedInCrawler:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search/?keywords=IT%20intern&location=South%20Korea"

    def _get_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _detect_intern_type(self, title):
        title_lower = title.lower()

        if "채용연계" in title or "conversion" in title_lower or "전환" in title:
            return "채용연계형"
        elif "체험" in title or "experience" in title_lower:
            return "체험형"
        elif "단기" in title or "short" in title_lower:
            return "단기인턴"
        elif "장기" in title or "long" in title_lower:
            return "장기인턴"
        else:
            return "일반인턴"

    def fetch_it_intern_jobs(self, max_jobs=30):
        driver = None
        all_jobs = []

        search_urls = [
            "https://www.linkedin.com/jobs/search/?keywords=software%20intern&location=South%20Korea",
            "https://www.linkedin.com/jobs/search/?keywords=developer%20intern&location=South%20Korea",
            "https://www.linkedin.com/jobs/search/?keywords=IT%20intern&location=South%20Korea"
        ]

        try:
            print("🔄 LinkedIn 크롤링 시작...")
            driver = self._get_driver()

            for url in search_urls:
                driver.get(url)
                time.sleep(3)

                for _ in range(2):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_cards = soup.select("div.base-card")[:max_jobs]

                for idx, card in enumerate(job_cards):
                    try:
                        title_elem = card.select_one("h3.base-search-card__title")
                        company_elem = card.select_one("h4.base-search-card__subtitle")
                        location_elem = card.select_one("span.job-search-card__location")
                        link_elem = card.select_one("a.base-card__full-link")

                        if not title_elem or not company_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        location = ""
                        if location_elem:
                            location = location_elem.get_text(strip=True)

                        job_url = ""
                        if link_elem:
                            job_url = link_elem.get('href', '')

                        intern_type = self._detect_intern_type(title)

                        all_jobs.append({
                            "job_id": "linkedin_" + str(idx) + "_" + str(int(time.time())),
                            "title": title,
                            "company": company,
                            "url": job_url,
                            "platform": "LinkedIn",
                            "location": location,
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

            print("✅ LinkedIn에서 " + str(len(unique_jobs)) + "개 IT 인턴 공고 수집 완료")
            return unique_jobs

        except Exception as e:
            print("❌ LinkedIn 크롤링 오류: " + str(e))
            return []
        finally:
            if driver:
                driver.quit()
