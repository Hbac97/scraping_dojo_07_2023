# Quote Scraper

This script is a web scraper that extracts quotes from a website and saves them to a JSON Lines file. It utilizes the Playwright library for web automation and BeautifulSoup for HTML parsing.

## Prerequisites

- Python 3.6+
- pip package manager

## Installation

1. Clone the repository:

git clone [<repository_url>](https://github.com/Hbac97/scraping_dojo_07_2023)

2. Install the required dependencies:

pip install -r requirements.txt

## Usage

1. The script uses environment variables to configure its behavior.

- `PROXY`: Proxy server address.
- `INPUT_URL`: URL of the website to scrape quotes from.
- `OUTPUT_FILE`: Output file path to save the scraped quotes.

2. Run the script:

python run.py

3. The script will start scraping quotes from the specified website. The scraping process will be displayed with progress updates. Once the scraping is complete, the quotes will be saved to the specified output file in JSON Lines format.

## License

This project is licensed under the [MIT License](LICENSE).
