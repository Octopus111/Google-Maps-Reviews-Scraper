import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as Soup

def scrape_google_maps_reviews(driver, business_name, address, postal_code):
    search_query = f"{business_name} {address} {postal_code}"
    driver.get('https://www.google.com/maps')

    try:
        # �����̼�
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # ������۰�ť
        try:
            reviews_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]'))
            )
            reviews_button.click()
        except TimeoutException:
            # ���û���ҵ����۰�ť��ֱ�ӷ��� None
            return None

        # ����ҳ���Լ�����������
        pane = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight", pane)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
            time.sleep(3)  # ���ӵȴ�ʱ�䣬ȷ�����ۼ������
            new_height = driver.execute_script("return arguments[0].scrollHeight", pane)
            if new_height == last_height:
                break
            last_height = new_height

        # ģ����"�鿴����"��ť��չ���������ۺͻظ�
        while True:
            try:
                more_buttons = driver.find_elements(By.CLASS_NAME, 'w8nwRe')
                if not more_buttons:
                    break
                for button in more_buttons:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)
            except Exception as e:
                print(f"Error clicking '�鿴����' button: {e}")
                break

        # ���ӵȴ�ʱ��ȷ���������ݼ������
        time.sleep(5)

        # ��ȡҳ��Դ����
        page_source = driver.page_source

        # ʹ��BeautifulSoup����ҳ��
        soup = Soup(page_source, "html.parser")

        # ��ȡ��������
        all_reviews = soup.find_all('div', class_='GHT2ce')

        if not all_reviews:
            return None

        reviews = []
        for review in all_reviews:
            # ��������
            try:
                star_element = review.find('span', class_='kvMYJc')
                star_rating = star_element.get('aria-label').split()[0]  # ��ȡ�Ǽ�����
            except AttributeError:
                star_rating = 'No rating'

            # ����ʱ��
            try:
                review_time = review.find('span', class_='rsqaWe').text.strip()
            except AttributeError:
                review_time = 'No date'

            # ��������
            try:
                review_text = review.find('span', class_='wiI7pd').text.strip()
            except AttributeError:
                review_text = 'No review text'

            # ���ۻظ��ͻظ�ʱ��
            try:
                review_reply_div = review.find('div', class_='CDe7pd')
                review_reply = review_reply_div.find('div', class_='wiI7pd').text.strip()
                review_reply_time = review_reply_div.find('span', class_='DZSIDd').text.strip()
            except AttributeError:
                review_reply = 'No reply'
                review_reply_time = 'No date'

            # ������Ч����
            if not (star_rating == 'No rating' and review_time == 'No date' and review_reply == 'No reply' and review_reply_time == 'No date'):
                reviews.append((review_text, star_rating, review_time, review_reply, review_reply_time))
        
        return reviews
    except TimeoutException as e:
        print(f"TimeoutException for {business_name} at {address}: {e}")
        return None

