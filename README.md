🛍️ Myntra Scraper Suite — Playwright + Selenium + Node.js Dashboard

A full-stack web automation project that scrapes Myntra brand and keyword listing pages using Playwright and Selenium, exports structured CSV datasets, and visualizes results via a Node.js dashboard.

📌 Features
🔵 Python Scrapers

Playwright automation (primary)

Selenium automation (secondary)

Infinite scroll handling

Retry + throttling logic

Anti-bot evasion (UA spoofing, pacing, HTTP/2 disable)

Advertisement vs Organic detection

DOM-based product ID extraction

Robust selector handling

CSV exports

🟢 Supported Pages

Brand pages:

Levi’s

Puma

Nike

Adidas

HRX

Keyword pages:

T-shirts

Shoes

Jeans

Dresses

Jackets

🟡 Node.js Dashboard

Lists all CSV outputs

Shows row counts

Click-to-preview tables

Highlights Ads vs Organic

Reads both Playwright & Selenium outputs

📁 Project Structure
Web-Scraper/
│
├── scrapers/
│   ├── playwright_runner.py
│   ├── playwright_debug.py
│   ├── selenium_runner.py
│
├── outputs/
│   ├── brand_nike.csv
│   ├── keyword_shoes.csv
│   └── ...
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
Scraping	Python, Playwright, Selenium
Browser Driver	Chromium, ChromeDriver
Data Export	CSV
Dashboard	Node.js, Express
Parsing	csv-parser
🧪 Data Extracted

Each CSV contains:

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

🚀 Setup Instructions
🐍 Python Environment

Create and activate venv:

python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\Activate.ps1  # Windows


Install deps:

pip install playwright selenium webdriver-manager pandas requests beautifulsoup4
playwright install

🌐 Node.js Setup

Inside server/:

npm install express csv-parser

▶️ How to Run
▶️ Playwright Runner

From project root:

python scrapers/playwright_runner.py


Generates:

outputs/
 ├ brand_*.csv
 └ keyword_*.csv

▶️ Selenium Runner
python scrapers/selenium_runner.py


Generates:

outputs_selenium/

▶️ Node Dashboard
cd server
node server.js


Open:

👉 http://localhost:3000

🧠 Key Design Decisions
✔ Infinite Scroll Strategy

Scroll to bottom

Wait 1 second

Recount cards

Stop after stagnation or 30 items

✔ Advertisement Detection

Uses DOM watermark:

.product-waterMark → "AD"

✔ Product ID

Extracted directly from:

<li id="34807146" class="product-base">

✔ Anti-Blocking Measures

Realistic user-agent

Retry navigation

Delay between pages

HTTP/2 disabled

Headless off for debugging

📄 Selector Strategy

Selectors are documented in:

docs/SELECTORS.md


Includes:

Card containers

Price fields

Ratings

Ad markers

CSV schema

🧑‍💻 Debug Utilities

playwright_debug.py is used for:

Testing selectors

DOM inspection

Screenshot capture

Diagnosing blocks

🏆 What This Demonstrates

This project showcases:

Browser automation

DOM inspection

Robust scraping pipelines

Multi-framework skill (Playwright + Selenium)

Retry & throttling systems

Data engineering

Full-stack integration

Documentation discipline

⚠️ Disclaimer

This project is built for educational and evaluation purposes only.
Respect website terms of service when scraping.

🙌 Author

Built by Ahill Pranav
For in-person automation / scraping evaluation rounds.