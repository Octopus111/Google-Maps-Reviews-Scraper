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
        # 搜索商家
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # 点击评论按钮
        try:
            reviews_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]'))
            )
            reviews_button.click()
        except TimeoutException:
            # 如果没有找到评论按钮，直接返回 None
            return None

        # 滚动页面以加载所有评论
        pane = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight", pane)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
            time.sleep(3)  # 增加等待时间，确保评论加载完成
            new_height = driver.execute_script("return arguments[0].scrollHeight", pane)
            if new_height == last_height:
                break
            last_height = new_height

        # 模拟点击"查看更多"按钮以展开完整评论和回复
        while True:
            try:
                more_buttons = driver.find_elements(By.CLASS_NAME, 'w8nwRe')
                if not more_buttons:
                    break
                for button in more_buttons:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)
            except Exception as e:
                print(f"Error clicking '查看更多' button: {e}")
                break

        # 增加等待时间确保所有内容加载完成
        time.sleep(5)

        # 获取页面源代码
        page_source = driver.page_source

        # 使用BeautifulSoup解析页面
        soup = Soup(page_source, "html.parser")

        # 获取所有评论
        all_reviews = soup.find_all('div', class_='GHT2ce')

        if not all_reviews:
            return None

        reviews = []
        for review in all_reviews:
            # 评论评分
            try:
                star_element = review.find('span', class_='kvMYJc')
                star_rating = star_element.get('aria-label').split()[0]  # 提取星级数字
            except AttributeError:
                star_rating = 'No rating'

            # 评论时间
            try:
                review_time = review.find('span', class_='rsqaWe').text.strip()
            except AttributeError:
                review_time = 'No date'

            # 评论内容
            try:
                review_text = review.find('span', class_='wiI7pd').text.strip()
            except AttributeError:
                review_text = 'No review text'

            # 评论回复和回复时间
            try:
                review_reply_div = review.find('div', class_='CDe7pd')
                review_reply = review_reply_div.find('div', class_='wiI7pd').text.strip()
                review_reply_time = review_reply_div.find('span', class_='DZSIDd').text.strip()
            except AttributeError:
                review_reply = 'No reply'
                review_reply_time = 'No date'

            # 过滤无效评论
            if not (star_rating == 'No rating' and review_time == 'No date' and review_reply == 'No reply' and review_reply_time == 'No date'):
                reviews.append((review_text, star_rating, review_time, review_reply, review_reply_time))
        
        return reviews
    except TimeoutException as e:
        print(f"TimeoutException for {business_name} at {address}: {e}")
        return None

