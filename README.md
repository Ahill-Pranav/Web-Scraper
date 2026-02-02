🛍️ Myntra Scraper Suite

Playwright + Selenium + Node.js Dashboard

A full-stack web automation project that scrapes Myntra brand and keyword listing pages using Playwright and Selenium, exports structured CSV datasets, and visualizes results via a Node.js dashboard.

This project was built for technical evaluation rounds to demonstrate:

DOM inspection

Dynamic scraping

Advertisement detection

Infinite scrolling

Lazy-loaded image handling

Multi-framework automation

Data engineering

Visualization

📌 Features
🔵 Python Scrapers

Playwright (primary)

Selenium (secondary)

Infinite scroll handling

Retry-based navigation

Lazy-loaded image hydration

Advertisement vs Organic classification

DOM-based extraction

CSV export

🟢 Supported Pages
Brand Pages

Levi’s

Puma

Nike

Adidas

HRX

Keyword Pages

T-shirts

Shoes

Jeans

Dresses

Jackets

🟡 Node.js Dashboard

Lists all CSV outputs

Preview tables

Row counts

Supports both Playwright & Selenium outputs

📁 Project Structure
Web-Scraper/
│
├── scrapers/
│   ├── playwright_runner.py
│   ├── selenium_runner.py
│
├── outputs/
│   ├── brand_nike.csv
│   └── keyword_shoes.csv
│
├── outputs_selenium/
│   └── ...
│
├── docs/
│   └── SELECTORS.md
│
├── server/
│   ├── server.js
│   ├── package.json
│   └── public/
│       └── style.css
│
├── README.md
└── requirements.txt

⚙️ Tech Stack
Layer	Technology
Automation	Python
Browsers	Playwright, Selenium
Parsing	DOM / CSS selectors
Output	CSV
Visualization	Node.js, Express
Dashboard Parsing	csv-parser
📊 Data Extracted

Each product record contains:

product_id
brand
product_name
image_url
selling_price
mrp_price
discount_percent
rating
comment_count
listing_type
source_page

📄 Scraping Strategy & Execution Guide
🔍 DOM Selectors Used

All data is collected directly from Myntra’s listing page DOM (no PDP navigation).

📦 Product Card Container
li.product-base

📊 Field Selectors
Field	Selector / Source
Brand	.product-brand
Product Name	.product-product
Selling Price	.product-discountedPrice OR .product-price
MRP	.product-strike
Discount	.product-discountPercentage
Rating	.product-ratingsContainer span
Review Count	.product-ratingsCount
Product ID	<li id="...">
Image URL	<picture><source srcset> OR <img src/data-src>

Images are lazy-loaded, so each product card is scrolled into view before extraction.

🟡 Advertisement vs Organic Detection

Sponsored products are identified purely from the DOM.

If a card contains:

.product-waterMark


with visible text:

AD


➡ classified as Advertisement

Otherwise ➝ Organic

No hardcoded values were used — detection is fully DOM-based.

🔄 Infinite Scrolling Strategy

Myntra loads products dynamically.

The scraper:

1️⃣ Counts visible product cards
2️⃣ Scrolls to bottom using:

window.scrollTo(0, document.body.scrollHeight)


3️⃣ Waits for new cards
4️⃣ Recounts
5️⃣ Repeats until ≥ 40 products are loaded or count stops increasing

Additionally:

• Each card is scrolled into view
• Short waits allow image hydration
• Prevents missing lazy-loaded images

▶️ How to Run the Project
🐍 Python Setup

Create and activate environment:

python -m venv .venv
.venv\Scripts\Activate.ps1


Install dependencies:

pip install playwright selenium webdriver-manager pandas requests beautifulsoup4
playwright install

▶️ Run Playwright Scraper
python scrapers/playwright_runner.py


Outputs:

outputs/

▶️ Run Selenium Scraper
python scrapers/selenium_runner.py


Outputs:

outputs_selenium/

▶️ Run Node.js Dashboard
cd server
npm install express csv-parser
node server.js


Open browser:

👉 http://localhost:3000

🧠 Key Engineering Decisions

DOM-first scraping (no APIs)

No PDP navigation

Retry-based page loading

Lazy image hydration

srcset parsing

Multi-framework implementation

Clean CSV schema for analysis

Visualization layer for validation

⚠️ Disclaimer

This project is for educational and evaluation purposes only.
Always respect website terms of service.

🙌 Author

Built by Ahill Pranav