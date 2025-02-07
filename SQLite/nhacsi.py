import string
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import none_of
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import sqlite3
#cau hinh chrom de chay nen
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")




def get_musician_links():
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://en.wikipedia.org/wiki/Lists_of_musicians"

    links = []  # Khởi tạo danh sách lưu các liên kết nhạc sĩ

    try:
        driver.get(url)


        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        list_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'List of')]")

        if list_links:
            print("Danh sách các đường link bắt đầu bằng 'List of':")
            for link in list_links:
                href = link.get_attribute('href')
                print(href)  # Print each link

            # Truy cập vào liên kết đầu tiên trong danh sách
            first_link = list_links[0].get_attribute('href')
            driver.get(first_link)

            # Đợi trang tải và kiểm tra số lượng thẻ <ul>
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "ul")))

            # Lấy tất cả các thẻ <ul>
            ul_tags = driver.find_elements(By.TAG_NAME, "ul")
            max_li_count = 0
            ul_musician = None

            # Tìm thẻ <ul> có nhiều <li> nhất
            for ul in ul_tags:
                li_tags = ul.find_elements(By.TAG_NAME, "li")
                if len(li_tags) > max_li_count:
                    max_li_count = len(li_tags)
                    ul_musician = ul

            if ul_musician:
                # Lấy tất cả các liên kết nhạc sĩ
                li_tags = ul_musician.find_elements(By.TAG_NAME, "li")
                for li in li_tags:
                    try:
                        a_tag = li.find_element(By.TAG_NAME, "a")
                        link = a_tag.get_attribute("href")
                        if "/wiki/" in link:  # Chỉ lấy các liên kết đến Wikipedia
                            links.append(link)
                    except Exception as e:
                        print(f"Không tìm thấy liên kết: {e}")

            # In ra số lượng liên kết nhạc sĩ tìm thấy
            print(f"Tổng số liên kết nhạc sĩ tìm thấy: {len(links)}")
        else:
            print("Không tìm thấy liên kết nào bắt đầu bằng 'List of'.")
    except Exception as e:
        print(f"Error accessing musician list: {e}")
    finally:
        driver.quit()

    return links  # Trả về danh sách các liên kết nhạc sĩ


#. Tạo cơ sở dữ liệu
conn = sqlite3.connect('musicians.db')
c = conn.cursor()
try:
    c.execute('''
        CREATE TABLE musicians (
            id integer primary key autoincrement,
            name text,
            years_active text
        )
    ''')
except Exception as e:
    print(e)

def them(name, years_active):
    conn = sqlite3.connect('musicians.db')
    c = conn.cursor()
    # Them vao co so du lieu
    c.execute('''
        INSERT INTO musicians(name, years_active)
        VALUES (:name, :years_active)
    ''',
      {
          'name': name,
          'years_active': years_active
      })
    conn.commit()
    conn.close()

def get_musicans_info(link):
    try:
        # Khoi tao webdriver
        driver = webdriver.Chrome(options=chrome_options)

        # mo trang
        driver.get(link)

        # Doi trang tai va dam bao the <h1> (ten ban nhac) xuat hien
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        # Lay ten ban nhac
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        # Lấy năm hoạt động
        try:
            years_active_element = driver.find_element(By.XPATH,
                                                       '//span[contains(text(),"Years active")]/parent::*/following-sibling::td')
            years_active = years_active_element.text
        except:
            years_active = ""

        them(name,years_active)
        return name, years_active

    except Exception as e:
        print(f"Lỗi khi truy cập {link}: {e}")
        return None

    finally:
        driver.quit()



musician_links = get_musician_links()
print(f"Thu thập được {len(musician_links)} ")
#
# su dung ThreadPoolExecutorde xu li cac thong tin song song
with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(get_musicans_info, musician_links))
