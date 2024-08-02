import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 配置ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
chromedriver_path = 'E:/chrome driver/chromedriver.exe'  # 请确保路径正确
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

