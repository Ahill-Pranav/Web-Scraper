from playwright.sync_api import sync_playwright
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
TARGET_COUNT = 40

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)


# ---------------- HELPERS ---------------- #
def hydrate_card_image(page, card):
    try:
        page.evaluate(
            "(el) => el.scrollIntoView({behavior: 'instant', block: 'center'})",
            card,
        )
        time.sleep(0.8)
    except:
        pass

def safe_text(card, sel):
    try:
        el = card.query_selector(sel)
        return el.inner_text().strip() if el else None
    except:
        return None


def extract_product(card, source_page):
    product_id = card.get_attribute("id")

    brand = safe_text(card, ".product-brand")
    name = safe_text(card, ".product-product")

    image_url = None

    # --- Try picture > source ---
    try:
        source = card.query_selector("picture source")
        if source:
            srcset = source.get_attribute("srcset")
            if srcset:
                image_url = srcset.split()[0]
    except:
        pass

    # --- Fallback to img ---
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


    selling = safe_text(card, ".product-discountedPrice") or safe_text(card, ".product-price")
    mrp = safe_text(card, ".product-strike")

    discount = safe_text(card, ".product-discountPercentage")

    rating = safe_text(card, ".product-ratingsContainer span")
    raw_count = safe_text(card, ".product-ratingsCount")
    comment_count = raw_count.replace("|", "").strip() if raw_count else None


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
        "source_page": source_page,
    }


def scroll_until_loaded(page):
    prev = 0
    stalls = 0

    while True:
        cards = page.query_selector_all(PRODUCT_SELECTOR)
        count = len(cards)
        print("   loaded:", count)

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
            page.wait_for_selector("li.product-base", timeout=20000)
            return True
        except Exception as e:
            print(f"   ⚠️ goto failed ({attempt+1}/{retries}): {e}")
            time.sleep(6)
    return False
# ---------------- MAIN ---------------- #

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-http2"]
            )
        context = browser.new_context(
            user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
         ),
    viewport={"width": 1280, "height": 900}
        )


        page = context.new_page()
        # -------- Brands -------- #
        for brand, url in BRAND_URLS.items():
            print(f"\n🔵 Scraping brand: {brand}")
            if not safe_goto(page, url):
                print("   ❌ Skipping:", url)
                continue

            time.sleep(4)
            cards = scroll_until_loaded(page)

                    
            rows = []
            for i, card in enumerate(cards[:TARGET_COUNT], 1):
                hydrate_card_image(page, card)

                row = extract_product(card, "brand")

                rows.append(row)


            out_file = OUT_DIR / f"brand_{brand}.csv"
            write_csv(out_file, rows)

            print(f"   ✅ saved {len(rows)} → {out_file}")

        # -------- Keywords -------- #
        for keyword, url in KEYWORD_URLS.items():
            print(f"\n🟢 Scraping keyword: {keyword}")
            if not safe_goto(page, url):
                print("   ❌ Skipping:", url)
                continue

            time.sleep(3)

            cards = scroll_until_loaded(page)

            rows = []
            for card in cards[:TARGET_COUNT]:
                rows.append(extract_product(card, "keyword"))

            out_file = OUT_DIR / f"keyword_{keyword}.csv"
            write_csv(out_file, rows)

            print(f"   ✅ saved {len(rows)} → {out_file}")

        browser.close()


if __name__ == "__main__":
    run()
