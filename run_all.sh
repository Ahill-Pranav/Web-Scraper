#!/bin/bash
echo "Running all scrapers..."
cd scrapers
python selenium_scraper.py
python playwright_scraper.py
cd ..
echo "Outputs in /outputs/"
