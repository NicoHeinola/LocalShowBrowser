import base64
import random
import traceback
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


class GoogleImageSearch:

    @staticmethod
    def bytes_to_base64(bytes):
        image = base64.b64encode(bytes).decode()
        return image

    @staticmethod
    def download_image(url: str):
        img_data = requests.get(url).content
        return img_data

    @staticmethod
    def fetch_image_urls(search_term: str = 'Cat', amount: int = 5, do_random: bool = True):

        options = Options()
        options.add_argument('--headless')

        driver = webdriver.Firefox(options=options)
        driver.get(f"https://www.google.com/search?q={search_term}&source=lnms&tbm=isch")

        try:
            urls = []

            # Accept / Reject cookies
            element = driver.find_elements(By.CSS_SELECTOR, ".VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.Nc7WLe")[1]
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(element))
            element.click()

            def delete_elements(driver, elements):
                for element in elements:
                    driver.execute_script("""
                    var element = arguments[0];
                    element.parentNode.removeChild(element);
                    """, element)

            delete_elements(driver, driver.find_elements(By.CSS_SELECTOR, '.isv-r.PNCib.iPukc.J3Tg1d'))  # Stupids ads
            delete_elements(driver, driver.find_elements(By.CSS_SELECTOR, '.KZ4CUc'))  # Top Suggestions
            delete_elements(driver, driver.find_elements(By.ID, 'kO001e'))  # Top search bar

            # Images page
            parent_element = driver.find_element(By.ID, 'islrg')
            links_containing_images = parent_element.find_elements(By.CSS_SELECTOR, '.wXeWr.islib.nfEiy')

            if do_random:
                random_images = links_containing_images[:]
                random.shuffle(random_images)
                for i in range(len(links_containing_images) - amount):
                    random_images.pop()
            else:
                random_images = [links_containing_images[i] for i in range(amount)]

            for image in random_images:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(image))
                image.click()

                # Get the src from opened high-res image
                selector = '/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a'

                try:
                    link_with_images = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, selector)))
                    high_resolution_image = WebDriverWait(link_with_images, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.r48jcc.pT0Scc.iPVvYb')))  # High res
                    # high_resolution_image = WebDriverWait(link_with_images, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.r48jcc.pT0Scc'))) # Low res
                except Exception as e:
                    print("EXCEPTION!")
                    traceback.print_exc()
                    continue

                url = high_resolution_image.get_attribute('src')
                urls.append(url)
        except Exception as e:
            print("EXCEPTION IN SEARCHING IMAGES:", traceback.format_exc())
            driver.close()
            return True, urls

        driver.close()
        return False, urls


if __name__ == '__main__':
    urls = GoogleImageSearch.fetch_image_urls('Demon Slayer', 50)
    # print(urls)
