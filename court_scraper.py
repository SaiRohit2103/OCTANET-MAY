import time
import json
import base64
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from PIL import Image
import pytesseract
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DelhiHighCourtScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        self.base_url = "https://delhihighcourt.nic.in/"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimal settings"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Install ChromeDriver automatically
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("WebDriver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise
    
    def solve_captcha(self, captcha_element):
        """Enhanced CAPTCHA solving with multiple methods"""
        try:
            # Method 1: Direct OCR on the CAPTCHA image
            captcha_screenshot = captcha_element.screenshot_as_png
            image = Image.open(io.BytesIO(captcha_screenshot))
            
            # Preprocess image for better OCR
            image_np = np.array(image)
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            
            # Apply various image processing techniques
            # 1. Threshold
            _, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # 2. Gaussian blur + threshold
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 3. Morphological operations
            kernel = np.ones((2, 2), np.uint8)
            morph = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel)
            
            # Try OCR on different processed images
            images_to_try = [gray, thresh1, thresh2, morph]
            
            for img in images_to_try:
                try:
                    # Configure Tesseract for better digit recognition
                    custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                    text = pytesseract.image_to_string(img, config=custom_config).strip()
                    
                    # Clean the text
                    text = ''.join(c for c in text if c.isalnum())
                    
                    if len(text) >= 4 and len(text) <= 8:  # Typical CAPTCHA length
                        logger.info(f"CAPTCHA solved: {text}")
                        return text
                        
                except Exception as e:
                    logger.warning(f"OCR attempt failed: {str(e)}")
                    continue
            
            # Method 2: Manual CAPTCHA solving (fallback)
            logger.warning("Automatic CAPTCHA solving failed, manual intervention required")
            
            # Save CAPTCHA image for manual review
            timestamp = int(time.time())
            captcha_path = f"captcha_{timestamp}.png"
            image.save(captcha_path)
            logger.info(f"CAPTCHA image saved as {captcha_path}")
            
            # For demo purposes, return a placeholder
            # In production, you might want to integrate with a CAPTCHA solving service
            return None
            
        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {str(e)}")
            return None
    
    def navigate_to_case_status(self):
        """Navigate to the case status page"""
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Look for case status or e-filing links
            case_status_links = [
                "//a[contains(text(), 'Case Status')]",
                "//a[contains(text(), 'case status')]",
                "//a[contains(text(), 'E-Filing')]",
                "//a[contains(text(), 'Online Services')]"
            ]
            
            for link_xpath in case_status_links:
                try:
                    link = self.driver.find_element(By.XPATH, link_xpath)
                    link.click()
                    time.sleep(3)
                    logger.info(f"Successfully clicked: {link_xpath}")
                    break
                except NoSuchElementException:
                    continue
            else:
                # If no direct link found, try to find case status in menu
                logger.warning("Direct case status link not found, exploring menu options")
                
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            raise
    
    def search_case(self, case_type, case_number, filing_year=""):
        """Main function to search for case details"""
        try:
            logger.info(f"Starting case search: {case_type} {case_number}/{filing_year}")
            
            # Navigate to case status page
            self.navigate_to_case_status()
            
            # Fill in case details
            result = self.fill_case_details(case_type, case_number, filing_year)
            
            if result:
                return {
                    'success': True,
                    'data': result,
                    'message': 'Case details retrieved successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to retrieve case details'
                }
                
        except Exception as e:
            logger.error(f"Case search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Search failed due to technical error'
            }
    
    def fill_case_details(self, case_type, case_number, filing_year):
        """Fill case details form and handle CAPTCHA"""
        try:
            max_attempts = 3
            
            for attempt in range(max_attempts):
                logger.info(f"Attempt {attempt + 1} to fill case details")
                
                # Find and fill case type dropdown
                try:
                    case_type_select = Select(self.driver.find_element(By.NAME, "case_type"))
                    case_type_select.select_by_visible_text(case_type)
                except:
                    # Try alternative selectors
                    case_type_input = self.driver.find_element(By.XPATH, "//select[contains(@name, 'type')] | //input[contains(@name, 'type')]")
                    if case_type_input.tag_name == "select":
                        Select(case_type_input).select_by_visible_text(case_type)
                    else:
                        case_type_input.send_keys(case_type)
                
                # Fill case number
                case_number_input = self.driver.find_element(By.XPATH, "//input[contains(@name, 'number')] | //input[contains(@placeholder, 'number')]")
                case_number_input.clear()
                case_number_input.send_keys(case_number)
                
                # Fill filing year if provided
                if filing_year:
                    try:
                        year_input = self.driver.find_element(By.XPATH, "//input[contains(@name, 'year')] | //select[contains(@name, 'year')]")
                        if year_input.tag_name == "select":
                            Select(year_input).select_by_visible_text(filing_year)
                        else:
                            year_input.clear()
                            year_input.send_keys(filing_year)
                    except NoSuchElementException:
                        logger.warning("Year field not found, continuing without it")
                
                # Handle CAPTCHA
                captcha_solved = self.handle_captcha()
                
                if captcha_solved:
                    # Submit the form
                    submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit'] | //button[contains(text(), 'Search')] | //button[contains(text(), 'Submit')]")
                    submit_button.click()
                    
                    # Wait for results
                    time.sleep(5)
                    
                    # Check if search was successful
                    if self.check_search_results():
                        return self.extract_case_details()
                    else:
                        logger.warning(f"Search attempt {attempt + 1} failed, retrying...")
                        continue
                else:
                    logger.warning(f"CAPTCHA solving failed on attempt {attempt + 1}")
                    continue
            
            logger.error("All search attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"Error filling case details: {str(e)}")
            return None
    
    def handle_captcha(self):
        """Handle CAPTCHA challenge"""
        try:
            # Look for CAPTCHA image
            captcha_selectors = [
                "//img[contains(@src, 'captcha')]",
                "//img[contains(@alt, 'captcha')]",
                "//img[contains(@id, 'captcha')]",
                "//img[contains(@class, 'captcha')]"
            ]
            
            captcha_element = None
            for selector in captcha_selectors:
                try:
                    captcha_element = self.driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not captcha_element:
                logger.warning("No CAPTCHA found, proceeding without solving")
                return True
            
            # Solve CAPTCHA
            captcha_text = self.solve_captcha(captcha_element)
            
            if captcha_text:
                # Find CAPTCHA input field
                captcha_input = self.driver.find_element(By.XPATH, "//input[contains(@name, 'captcha')] | //input[contains(@placeholder, 'captcha')] | //input[contains(@id, 'captcha')]")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                
                logger.info("CAPTCHA solved and entered successfully")
                return True
            else:
                logger.error("Failed to solve CAPTCHA")
                return False
                
        except Exception as e:
            logger.error(f"CAPTCHA handling error: {str(e)}")
            return False
    
    def check_search_results(self):
        """Check if search returned valid results"""
        try:
            # Look for common success indicators
            success_indicators = [
                "//table",
                "//div[contains(@class, 'result')]",
                "//div[contains(text(), 'Case Details')]",
                "//span[contains(text(), 'Found')]"
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            
            # Check for error messages
            error_indicators = [
                "//div[contains(text(), 'No record found')]",
                "//span[contains(text(), 'Invalid')]",
                "//div[contains(text(), 'Error')]"
            ]
            
            for indicator in error_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        logger.warning(f"Error found: {element.text}")
                        return False
                except NoSuchElementException:
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking search results: {str(e)}")
            return False
    
    def extract_case_details(self):
        """Extract case details from the results page"""
        try:
            case_data = {
                'parties': [],
                'hearings': [],
                'orders': [],
                'filing_date': '',
                'status': '',
                'case_number': '',
                'raw_html': self.driver.page_source
            }
            
            # Extract case number
            try:
                case_num_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Case No')] | //th[contains(text(), 'Case No')]")
                case_data['case_number'] = case_num_element.find_element(By.XPATH, "following-sibling::td").text.strip()
            except:
                pass
            
            # Extract parties
            try:
                party_elements = self.driver.find_elements(By.XPATH, "//td[contains(text(), 'Petitioner')] | //td[contains(text(), 'Respondent')] | //td[contains(text(), 'Appellant')]")
                for element in party_elements:
                    case_data['parties'].append(element.text.strip())
            except:
                pass
            
            # Extract filing date
            try:
                filing_date_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Filing Date')] | //td[contains(text(), 'Date of Filing')]")
                case_data['filing_date'] = filing_date_element.find_element(By.XPATH, "following-sibling::td").text.strip()
            except:
                pass
            
            # Extract status
            try:
                status_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Status')] | //td[contains(text(), 'Case Status')]")
                case_data['status'] = status_element.find_element(By.XPATH, "following-sibling::td").text.strip()
            except:
                pass
            
            # Extract hearings/orders from tables
            try:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            row_data = [cell.text.strip() for cell in cells]
                            # Categorize based on content
                            if any(keyword in ' '.join(row_data).lower() for keyword in ['hearing', 'next date', 'adjourned']):
                                case_data['hearings'].append(row_data)
                            elif any(keyword in ' '.join(row_data).lower() for keyword in ['order', 'judgment', 'disposed']):
                                case_data['orders'].append(row_data)
            except:
                pass
            
            logger.info("Case details extracted successfully")
            return case_data
            
        except Exception as e:
            logger.error(f"Error extracting case details: {str(e)}")
            return {
                'error': str(e),
                'raw_html': self.driver.page_source
            }
    
    def close(self):
        """Close the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    scraper = DelhiHighCourtScraper()
    try:
        result = scraper.search_case("WP(C)", "12345", "2023")
        print(json.dumps(result, indent=2))
    finally:
        scraper.close()