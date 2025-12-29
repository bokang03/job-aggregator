from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


class JobKoreaCrawler:
    def __init__(self):
        self.base_url = "https://www.jobkorea.co.kr/Search/?stext=백엔드개발자&tabType=recruit"

    def _get_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def fetch_backend_jobs(self, max_jobs=30):
        driver = None
        try:
            print("🔄 잡코리아 크롤링 시작...")
            driver = self._get_driver()
            driver.get(self.base_url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_items = soup.select("article.list-item")[:max_jobs]

            if not job_items:
                job_items = soup.select("li.list-post")[:max_jobs]

            result = []
            for idx, item in enumerate(job_items):
                try:
                    title_elem = item.select_one("a.information-title-link") or item.select_one("a.title")
                    company_elem = item.select_one("a.company-name-link") or item.select_one("a.name")

                    if not title_elem or not company_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    href = title_elem.get('href', '')

                    if not href.startswith('http'):
                        job_url = "https://www.jobkorea.co.kr" + href
                    else:
                        job_url = href

                    result.append({
                        "job_id": f"jobkorea_{idx}_{int(time.time())}",
                        "title": title,
                        "company": company,
                        "url": job_url,
                        "platform": "잡코리아",
                        "location": "",
                        "experience": "",
                        "education": "",
                        "salary": "",
                        "deadline": ""
                    })

                except Exception as e:
                    continue

            print(f"✅ 잡코리아에서 {len(result)}개 공고 수집 완료")
            return result

        except Exception as e:
            print(f"❌ 잡코리아 크롤링 오류: {e}")
            return []
        finally:
            if driver:
                driver.quit()
