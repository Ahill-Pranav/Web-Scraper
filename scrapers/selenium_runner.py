from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from pathlib import Path

# ---------------- CONFIG ---------------- #

BRAND_URLS = {
    "levis": "https://www.myntra.com/levis",
    "puma": "https://www.myntra.com/puma",
    "nike": "https://www.myntra.com/nike",
    "adidas": "https://www.myntra.com/adidas",
    "hrx": "https://www.myntra.com/hrx",
}

KEYWORD_URLS = {
    "tshirt": "https://www.myntra.com/tshirt?rawQuery=tshirt",
    "shoes": "https://www.myntra.com/shoes?rawQuery=shoes",
    "jeans": "https://www.myntra.com/jeans?rawQuery=jeans",
    "dresses": "https://www.myntra.com/dresses?rawQuery=dresses",
    "jackets": "https://www.myntra.com/jackets?rawQuery=jackets",
}

PRODUCT_SELECTOR = "li.product-base"
TARGET_COUNT = 30

OUT_DIR = Path("outputs_selenium")
OUT_DIR.mkdir(exist_ok=True)


# ---------------- HELPERS ---------------- #

def start_driver():
    opts = Options()
    opts.add_argument("--disable-http2")
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_page_load_timeout(90)
    return driver


def safe_get(driver, url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            time.sleep(4)
            driver.find_element(By.CSS_SELECTOR, PRODUCT_SELECTOR)
            return True
        except Exception as e:
            print(f"   ⚠️ get failed ({attempt+1}/{retries}): {e}")
            time.sleep(6)
    return False


def scroll_until_loaded(driver):
    prev = 0
    stalls = 0

    while True:
        cards = driver.find_elements(By.CSS_SELECTOR, PRODUCT_SELECTOR)
        count = len(cards)
        print("   loaded:", count)

        if count >= TARGET_COUNT:
            return cards

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        if count == prev:
            stalls += 1
            if stalls > 6:
                return cards
        else:
            stalls = 0

        prev = count


def safe_text(elem, sel):
    try:
        return elem.find_element(By.CSS_SELECTOR, sel).text.strip()
    except:
        return None


def extract_product(card, source_page):
    product_id = card.get_attribute("id")

    brand = safe_text(card, ".product-brand")
    name = safe_text(card, ".product-product")

    try:
        img = card.find_element(By.TAG_NAME, "img")
        image_url = img.get_attribute("src")
    except:
        image_url = None

    selling = safe_text(card, ".product-discountedPrice") or safe_text(card, ".product-price")
    mrp = safe_text(card, ".product-strike")

    discount = safe_text(card, ".product-discountPercentage")

    rating = safe_text(card, ".product-ratingsContainer span")
    comment_count = safe_text(card, ".product-ratingsCount")

    try:
        watermark = card.find_element(By.CSS_SELECTOR, ".product-waterMark")
        listing_type = "Advertisement" if "AD" in watermark.text else "Organic"
    except:
        listing_type = "Organic"

    return {
        "product_id": product_id,
        "brand": brand,
        "product_name": name,
        "image_url": image_url,
        "selling_price": selling,
        "mrp_price": mrp,
        "discount_percent": discount,
        "rating": rating,
        "comment_count": comment_count,
        "listing_type": listing_type,
        "source_page": source_page,
    }


def write_csv(path, rows):
    keys = [
        "product_id",
        "brand",
        "product_name",
        "image_url",
        "selling_price",
        "mrp_price",
        "discount_percent",
        "rating",
        "comment_count",
        "listing_type",
        "source_page",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


# ---------------- MAIN ---------------- #

def run():
    driver = start_driver()

    for brand, url in BRAND_URLS.items():
        print(f"\n🔵 Scraping brand: {brand}")

        if not safe_get(driver, url):
            print("   ❌ Skipping:", url)
            continue

        cards = scroll_until_loaded(driver)

        rows = [extract_product(c, "brand") for c in cards[:TARGET_COUNT]]

        out_file = OUT_DIR / f"brand_{brand}.csv"
        write_csv(out_file, rows)

        print(f"   ✅ saved {len(rows)} → {out_file}")
        time.sleep(5)

    for keyword, url in KEYWORD_URLS.items():
        print(f"\n🟢 Scraping keyword: {keyword}")

        if not safe_get(driver, url):
            print("   ❌ Skipping:", url)
            continue

        cards = scroll_until_loaded(driver)

        rows = [extract_product(c, "keyword") for c in cards[:TARGET_COUNT]]

        out_file = OUT_DIR / f"keyword_{keyword}.csv"
        write_csv(out_file, rows)

        print(f"   ✅ saved {len(rows)} → {out_file}")
        time.sleep(5)

    driver.quit()


if __name__ == "__main__":
    run()
