# Web Data Scraper with Selenium and BeautifulSoup

This project automates the process of logging into a website, navigating through a member directory or search results, scraping structured data (e.g. names and addresses), and saving it to a local file. It also includes a script to post-process an Excel file by filling in address information from the scraped data.

## Features

- Automated login using Selenium
- Country-based filtering and pagination support
- Scrapes name-address pairs from a directory listing
- Skips empty or no-result searches to improve speed
- Gracefully handles network errors and partial interruptions
- Saves extracted data to a local file as a Python dictionary
- Fills an Excel file's missing "Address" column using the scraped data

## Technologies Used

- Python 3.9+
- Selenium
- BeautifulSoup (bs4)
- `openpyxl` for Excel processing
- `.env` file support via `python-dotenv`

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/member-directory-scraper.git
cd member-directory-scraper

python -m venv venv
source venv/bin/activate     # On Windows use: venv\Scripts\activate

USERNAME=your@email.com
PASSWORD=yourPassword123!
CHROME_DRIVER_PATH=/path/to/chromedriver

python main.py
