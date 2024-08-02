import os
import pandas as pd
from config import driver
from data_loader import data
from scrape_reviews import scrape_google_maps_reviews

# 爬取所有商家的评论
for index, row in data.iterrows():
    business_name = row['Name']
    address = row['Address']
    postal_code = row['Postcode']
    print(f"Processing {business_name}...")
    reviews = scrape_google_maps_reviews(driver, business_name, address, postal_code)
    if reviews is None:
        print(f"No reviews for {business_name}. Skipping...")
        output_file_name = f"{business_name}_{address}_no_reviews.csv".replace(" ", "_").replace("/", "_")
        with open(f'C:/Users/ASUS/Desktop/{output_file_name}', 'w') as f:
            f.write(f"No reviews for {business_name} at {address}")
    else:
        all_reviews = []
        for review in reviews:
            all_reviews.append([business_name, address, postal_code] + list(review))
        
        # 保存结果到CSV文件
        output_file_name = f"{business_name}_{address}.csv".replace(" ", "_").replace("/", "_")
        output_path = f'C:/Users/ASUS/Desktop/{output_file_name}'
        reviews_df = pd.DataFrame(all_reviews, columns=['Name', 'Address', 'Postcode', 'Review', 'Rating', 'Review Time', 'Reply', 'Reply Time'])
        reviews_df.to_csv(output_path, index=False, encoding='utf-8-sig')

# 关闭浏览器
driver.quit()

