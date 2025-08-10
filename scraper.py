from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import re
from config import Config

class CourtScraper:
    def __init__(self):
        """Initialize the web scraper with Chrome options"""
        self.chrome_options = Options()
        
        # Add Chrome options for better stability
        for option in Config.CHROME_OPTIONS:
            self.chrome_options.add_argument(option)
        
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        """Start the Chrome driver"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("🚀 Chrome driver started successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to start Chrome driver: {str(e)}")
            return False
    
    def search_case(self, case_type, case_number, filing_year):
        """
        Main method to search for a case
        This is a DEMO implementation - you'll need to adapt it to the actual court website
        """
        if not self.start_driver():
            return {"error": "Failed to start web driver"}
        
        try:
            print(f"🔍 Searching for case: {case_type} {case_number}/{filing_year}")
            
            # Navigate to court website
            self.driver.get(Config.COURT_URL)
            print(f"📄 Navigated to: {Config.COURT_URL}")
            
            # Wait for page to load
            time.sleep(3)
            
            # Since we can't access the real court website structure,
            # this is a DEMO implementation
            # You'll need to inspect the actual website and modify these selectors
            
            # DEMO: Try to find case status or search links
            case_data = self._demo_search_implementation(case_type, case_number, filing_year)
            
            return case_data
            
        except TimeoutException:
            return {"error": "Website took too long to respond. Please try again."}
        except NoSuchElementException as e:
            return {"error": f"Could not find required elements on the page: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser closed")
    
    def _demo_search_implementation(self, case_type, case_number, filing_year):
        """
        DEMO implementation - replace this with actual website scraping
        """
        try:
            # Get page source for parsing
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # DEMO: Return sample data since we can't access real court data
            demo_case_data = {
                "petitioner": f"Sample Petitioner for {case_type} {case_number}",
                "respondent": f"Sample Respondent for {case_type} {case_number}",
                "filing_date": f"01/01/{filing_year}",
                "next_hearing_date": "15/12/2024",
                "status": "Under Hearing",
                "pdf_links": [
                    {
                        "title": "Order dated 10/11/2024",
                        "url": "#demo-link-1"
                    },
                    {
                        "title": "Judgment dated 05/10/2024", 
                        "url": "#demo-link-2"
                    }
                ],
                "raw_html": str(soup)[:1000]  # Store first 1000 chars for debugging
            }
            
            print("✅ Demo case data generated successfully!")
            return demo_case_data
            
        except Exception as e:
            return {"error": f"Error in demo search: {str(e)}"}
    
    def _find_case_status_section(self):
        """
        Helper method to find the case status section
        MODIFY THIS based on actual website structure
        """
        possible_selectors = [
            "//a[contains(text(), 'Case Status')]",
            "//a[contains(text(), 'Search Case')]",
            "//a[contains(text(), 'Case Search')]",
            "//link[contains(@href, 'case')]",
        ]
        
        for selector in possible_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                return element
            except:
                continue
        return None
    
    def _fill_search_form(self, case_type, case_number, filing_year):
        """
        Helper method to fill the search form
        MODIFY THIS based on actual website structure
        """
        try:
            # These are example selectors - modify based on actual website
            
            # Select case type
            case_type_selector = self.driver.find_element(By.NAME, "case_type")
            Select(case_type_selector).select_by_visible_text(case_type)
            
            # Enter case number
            case_number_field = self.driver.find_element(By.NAME, "case_number")
            case_number_field.clear()
            case_number_field.send_keys(case_number)
            
            # Enter filing year
            year_field = self.driver.find_element(By.NAME, "filing_year")
            year_field.clear()
            year_field.send_keys(str(filing_year))
            
            # Submit form
            submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
            submit_button.click()
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling form: {str(e)}")
            return False
    
    def _parse_case_results(self):
        """
        Helper method to parse case results from the results page
        MODIFY THIS based on actual website structure
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        case_data = {
            "petitioner": self._extract_text_by_label(soup, "petitioner"),
            "respondent": self._extract_text_by_label(soup, "respondent"), 
            "filing_date": self._extract_text_by_label(soup, "filing"),
            "next_hearing_date": self._extract_text_by_label(soup, "hearing"),
            "status": self._extract_text_by_label(soup, "status"),
            "pdf_links": self._extract_pdf_links(soup),
            "raw_html": str(soup)
        }
        
        return case_data
    
    def _extract_text_by_label(self, soup, label_keyword):
        """Extract text based on label keywords"""
        # This is a generic helper - modify based on actual HTML structure
        try:
            # Look for labels containing the keyword
            label = soup.find(text=re.compile(label_keyword, re.I))
            if label and label.parent:
                return label.parent.get_text().strip()
            return "Not found"
        except:
            return "Error extracting"
    
    def _extract_pdf_links(self, soup):
        """Extract PDF download links"""
        pdf_links = []
        try:
            # Look for PDF links
            links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
            for link in links:
                pdf_links.append({
                    "title": link.get_text().strip() or "PDF Document",
                    "url": link.get('href')
                })
        except:
            pass
        
        return pdf_links

# Utility function to test the scraper
def test_scraper():
    """Test function to check if scraper works"""
    scraper = CourtScraper()
    result = scraper.search_case("Civil", "12345", 2024)
    print("Test Result:", result)
    return result

if __name__ == "__main__":
    test_scraper()
