from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


class LinkedInCrawler:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search/?keywords=backend%20developer&location=South%20Korea"

    def _get_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def fetch_backend_jobs(self, max_jobs=20):
        driver = None
        try:
            print("🔄 LinkedIn 크롤링 시작...")
            driver = self._get_driver()
            driver.get(self.base_url)
            time.sleep(3)

            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.select("div.base-card")[:max_jobs]

            result = []
            for idx, card in enumerate(job_cards):
                try:
                    title_elem = card.select_one("h3.base-search-card__title")
                    company_elem = card.select_one("h4.base-search-card__subtitle")
                    location_elem = card.select_one("span.job-search-card__location")
                    link_elem = card.select_one("a.base-card__full-link")

                    if not title_elem or not company_elem:
                        continue

                    result.append({
                        "job_id": f"linkedin_{idx}_{int(time.time())}",
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True),
                        "url": link_elem.get('href', '') if link_elem else "",
                        "platform": "LinkedIn",
                        "location": location_elem.get_text(strip=True) if location_elem else "",
                        "experience": "",
                        "education": "",
                        "salary": "",
                        "deadline": ""
                    })

                except Exception:
                    continue

            print(f"✅ LinkedIn에서 {len(result)}개 공고 수집 완료")
            return result

        except Exception as e:
            print(f"❌ LinkedIn 크롤링 오류: {e}")
            return []
        finally:
            if driver:
                driver.quit()
