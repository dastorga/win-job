from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import List, Dict, Optional
from app.models.models import Job, ScrapeLog
from app.database.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, headless: bool = True):
        self.setup_driver(headless)
        self.base_url = "https://www.linkedin.com"
        
    def setup_driver(self, headless: bool):
        """Configure Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def search_jobs(self, 
                   search_term: str = "DevOps", 
                   location: str = "España", 
                   max_jobs: int = 50) -> List[Dict]:
        """
        Search for jobs on LinkedIn
        """
        jobs_data = []
        
        try:
            # Build search URL
            search_url = f"{self.base_url}/jobs/search?"
            search_url += f"keywords={search_term.replace(' ', '%20')}"
            if location and location.lower() != "worldwide":
                search_url += f"&location={location.replace(' ', '%20')}"
            search_url += "&f_TPR=r86400"  # Last 24 hours
            search_url += "&f_JT=F"  # Full-time only
            search_url += "&f_WRA=true"  # Remote jobs
            
            logger.info(f"Searching jobs with URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait for job results to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
            )
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs(max_jobs)
            
            # Get job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            logger.info(f"Found {len(job_cards)} job cards")
            
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        # Check if requires English
                        job_data['requires_english'] = self._check_english_requirement(job_data)
                        jobs_data.append(job_data)
                        
                except Exception as e:
                    logger.error(f"Error extracting job {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in job search: {e}")
            
        return jobs_data
    
    def _scroll_to_load_jobs(self, max_jobs: int):
        """Scroll page to load more job results"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if we have enough jobs
            current_jobs = len(self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card"))
            if current_jobs >= max_jobs:
                break
                
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def _extract_job_data(self, job_card) -> Optional[Dict]:
        """Extract job data from a job card element"""
        try:
            # Click on job card to load details
            job_card.click()
            time.sleep(1)
            
            # Wait for job details to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__job-details"))
            )
            
            # Extract basic information
            title_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__title")
            company_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle")
            location_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
            
            # Get LinkedIn job URL and ID
            job_link = title_elem.find_element(By.TAG_NAME, "a").get_attribute("href")
            job_id = self._extract_job_id_from_url(job_link)
            
            # Extract job details from the details panel
            job_details = self.driver.find_element(By.CLASS_NAME, "jobs-search__job-details")
            description_elem = job_details.find_element(By.CSS_SELECTOR, ".jobs-description-content__text")
            
            # Parse description with BeautifulSoup for better text extraction
            soup = BeautifulSoup(description_elem.get_attribute("innerHTML"), 'html.parser')
            description = soup.get_text(separator='\n', strip=True)
            
            # Extract additional details
            job_criteria = job_details.find_elements(By.CSS_SELECTOR, ".job-criteria__text")
            employment_type = job_criteria[0].text.strip() if len(job_criteria) > 0 else None
            seniority_level = job_criteria[1].text.strip() if len(job_criteria) > 1 else None
            
            return {
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip(),
                'location': location_elem.text.strip(),
                'description': description,
                'employment_type': employment_type,
                'seniority_level': seniority_level,
                'linkedin_job_id': job_id,
                'linkedin_url': job_link,
                'posted_date': self._extract_posted_date(job_details),
            }
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def _extract_job_id_from_url(self, url: str) -> str:
        """Extract LinkedIn job ID from URL"""
        match = re.search(r'/view/(\d+)/', url)
        return match.group(1) if match else ""
    
    def _extract_posted_date(self, job_details) -> Optional[datetime]:
        """Extract and parse job posting date"""
        try:
            time_elem = job_details.find_element(By.CSS_SELECTOR, "time")
            datetime_str = time_elem.get_attribute("datetime")
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()
    
    def _check_english_requirement(self, job_data: Dict) -> bool:
        """
        Analyze job description to determine if English is required
        """
        text_to_check = f"{job_data['title']} {job_data['description']}".lower()
        
        # English requirement keywords
        english_keywords = [
            'english', 'inglés', 'ingles', 'native english', 'fluent english',
            'english speaking', 'english proficiency', 'bilingual',
            'international team', 'global team', 'multinational'
        ]
        
        # Check for English requirements
        for keyword in english_keywords:
            if keyword in text_to_check:
                return True
                
        return False
    
    def save_jobs_to_database(self, jobs_data: List[Dict], db: Session):
        """Save scraped jobs to database"""
        saved_count = 0
        
        for job_data in jobs_data:
            try:
                # Check if job already exists
                existing_job = db.query(Job).filter(
                    Job.linkedin_job_id == job_data['linkedin_job_id']
                ).first()
                
                if not existing_job:
                    job = Job(**job_data)
                    db.add(job)
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving job to database: {e}")
                continue
        
        try:
            db.commit()
            logger.info(f"Saved {saved_count} new jobs to database")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing jobs to database: {e}")
            
        return saved_count
    
    def close(self):
        """Close the webdriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def __del__(self):
        self.close()


def search_multiple_regions(search_term: str = "DevOps", max_jobs_per_region: int = 20) -> Dict:
    """Search jobs across multiple Spanish-speaking regions"""
    regions = [
        "España", "México", "Argentina", "Colombia", "Chile", 
        "Perú", "Uruguay", "Costa Rica", "Remote"
    ]
    
    all_jobs = []
    scraper = LinkedInScraper()
    
    try:
        for region in regions:
            logger.info(f"Searching in {region}...")
            jobs = scraper.search_jobs(search_term, region, max_jobs_per_region)
            
            # Add region tag to jobs
            for job in jobs:
                job['search_region'] = region
                
            all_jobs.extend(jobs)
            
            # Rate limiting - wait between regions
            time.sleep(3)
            
    except Exception as e:
        logger.error(f"Multi-region search failed: {e}")
    finally:
        scraper.close()
    
    return {
        'success': True,
        'jobs_found': len(all_jobs),
        'regions_searched': regions,
        'jobs_data': all_jobs
    }

def scrape_linkedin_jobs(search_term: str = "DevOps", 
                        location: str = "España", 
                        max_jobs: int = 50) -> Dict:
    """
    Main function to scrape LinkedIn jobs and save to database
    """
    db = next(get_db())
    scraper = LinkedInScraper()
    
    # Create scrape log
    scrape_log = ScrapeLog(
        search_term=search_term,
        location=location,
        started_at=datetime.utcnow()
    )
    
    try:
        # Scrape jobs
        jobs_data = scraper.search_jobs(search_term, location, max_jobs)
        
        # Save to database
        saved_count = scraper.save_jobs_to_database(jobs_data, db)
        
        # Update scrape log
        scrape_log.jobs_found = len(jobs_data)
        scrape_log.jobs_saved = saved_count
        scrape_log.success = True
        scrape_log.completed_at = datetime.utcnow()
        
        result = {
            'success': True,
            'jobs_found': len(jobs_data),
            'jobs_saved': saved_count,
            'jobs_without_english': len([j for j in jobs_data if not j['requires_english']])
        }
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        scrape_log.success = False
        scrape_log.error_message = str(e)
        scrape_log.completed_at = datetime.utcnow()
        
        result = {
            'success': False,
            'error': str(e)
        }
    
    finally:
        # Save scrape log
        db.add(scrape_log)
        db.commit()
        db.close()
        scraper.close()
    
    return result