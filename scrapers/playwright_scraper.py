from multiprocessing import context
from playwright.sync_api import sync_playwright
import time
import csv
import re
from pathlib import Path

URL = "https://www.myntra.com/nike"
SOURCE_PAGE = "brand"

PRODUCT_SELECTOR = "li.product-base"
OUTPUT_FILE = Path("outputs/nike_brand_playwright.csv")

OUTPUT_FILE.parent.mkdir(exist_ok=True)

TARGET_COUNT = 40

def hydrate_card_image(page, card):
    try:
        page.evaluate("(el) => el.scrollIntoView({behavior: 'instant', block: 'center'})", card)
        time.sleep(0.8)
    except:
        pass

def safe_text(card, sel):
    try:
        el = card.query_selector(sel)
        return el.inner_text().strip() if el else None
    except:
        return None


def extract_product(card):
    # product id from li attribute
    product_id = card.get_attribute("id")

    brand = safe_text(card, ".product-brand")
    name = safe_text(card, ".product-product")

    image_url = None

    # --- Try picture > source (preferred) ---
    try:
        source = card.query_selector("picture source")
        if source:
            srcset = source.get_attribute("srcset")
            if srcset:
                # Take the first URL before the size descriptor
                image_url = srcset.split()[0]
    except:
        pass

    # --- Fallback to img attributes ---
    if not image_url:
        try:
            img = card.query_selector("img")
            if img:
                image_url = (
                    img.get_attribute("src")
                    or img.get_attribute("data-src")
                    or img.get_attribute("data-srcset")
                )
        except:
            pass




    # prices
    selling = safe_text(card, ".product-discountedPrice") or safe_text(card, ".product-price")
    mrp = safe_text(card, ".product-strike")

    discount = safe_text(card, ".product-discountPercentage")

    # rating
    rating = safe_text(card, ".product-ratingsContainer span")

    # comment count (plural!)
    comment_count = safe_text(card, ".product-ratingsCount")

    # advertisement detection
    listing_type = "Advertisement"
    try:
        watermark = card.query_selector(".product-waterMark")
        if not watermark or "AD" not in watermark.inner_text():
            listing_type = "Organic"
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
        "source_page": SOURCE_PAGE,
    }


def scroll_until_loaded(page):
    prev = 0
    stalls = 0

    while True:
        cards = page.query_selector_all(PRODUCT_SELECTOR)
        count = len(cards)
        print("Loaded cards:", count)

        if count >= TARGET_COUNT:
            return cards

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        if count == prev:
            stalls += 1
            if stalls > 6:
                return cards
        else:
            stalls = 0

        prev = count


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

def safe_goto(page, url, retries=3):
    for attempt in range(retries):
        try:
            page.goto(url, timeout=90000, wait_until="domcontentloaded")
            page.wait_for_selector(PRODUCT_SELECTOR, timeout=20000)
            return True
        except Exception as e:
            print(f"⚠️ goto failed ({attempt+1}/{retries}): {e}")
            time.sleep(6)
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()


        if not safe_goto(page, URL):
            print("❌ Failed to load page after retries")
            browser.close()
            return

        cards = scroll_until_loaded(page)

        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)


        rows = []
        for i, card in enumerate(cards[:TARGET_COUNT], 1):
            hydrate_card_image(page, card)

            row = extract_product(card)

            if not row["image_url"]:
                print("Missing image:", i, row["product_name"])

            rows.append(row)


        write_csv(OUTPUT_FILE, rows)

        print(f"\n✅ Saved {len(rows)} products to {OUTPUT_FILE}")

        browser.close()


if __name__ == "__main__":
    main()
