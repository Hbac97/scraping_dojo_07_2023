import os
import subprocess
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import jsonlines
import asyncio
import requests
from urllib.parse import urljoin, urlparse

class QuoteScraper:
    def __init__(self):

        if not os.path.exists(".env"):
            print("The .env file does not exist. Make sure to create it with the required environment variables.")
            exit(1)

        load_dotenv()
        self.proxy = os.getenv("PROXY")
        self.input_url = os.getenv("INPUT_URL")
        self.output_file = os.getenv("OUTPUT_FILE")
        self.base_url = self.get_base_url(self.input_url)

        try:
            print(f"Preparing drivers...")
            subprocess.call("playwright install chromium", shell=True)
        except Exception as e:
            print(f"Error during Playwright installation: {e}")
            exit(1)

    async def run(self):
        print("Starting scraping process...")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True, proxy=self.get_proxy_config())
            context = await browser.new_context()

            await self.scrape_quotes(context)

            await context.close()
            await browser.close()

        print("Scraping process completed.")

    def get_proxy_config(self):
        if self.proxy:
            proxy_parts = self.proxy.split("@")
            if len(proxy_parts) == 2:
                proxy_auth = proxy_parts[0].split(":")
                if len(proxy_auth) == 2:
                    username = proxy_auth[0]
                    password = proxy_auth[1]
                    proxy_server = proxy_parts[1]
                    return {
                        "server": proxy_server,
                        "username": username,
                        "password": password
                    }
            return {
                "server": self.proxy
            }
        return None

    async def scrape_quotes(self, context):
        quotes = []

        page = await context.new_page()
        delay_value = self.get_initial_delay() or 10

        while True:
            print(f"Scraping quotes from: {self.input_url}")
            await page.goto(self.input_url)
            await asyncio.sleep(delay_value+2)

            page_content = await page.content()

            soup = BeautifulSoup(page_content, "html.parser")


            quote_elements = soup.find_all(class_="quote")
            if not quote_elements:
                print("No quotes found. Stopping scraping.")
                break

            for quote_element in quote_elements:
                text = quote_element.find(class_="text").get_text()
                author = quote_element.find(class_="author").get_text()
                tags = [tag.get_text() for tag in quote_element.find_all(class_="tag")]

                quote = {"text": text, "by": author, "tags": tags}
                quotes.append(quote)

            next_page = soup.find(class_="next")
            if not next_page:
                print("No next page found. Stopping scraping.")
                break

            next_page_url = next_page.find("a")["href"]
            self.input_url = urljoin(self.base_url, next_page_url)

        self.save_quotes(quotes)

    def get_initial_delay(self):
        page = requests.get(self.input_url)
        soup = BeautifulSoup(page.content, "html.parser")
        script = soup.find("script", string=re.compile(r"delayInMilliseconds\s*=\s*\d+"))
        if script:
            delay_code = script.text.strip()
            delay_value = int(re.search(r"delayInMilliseconds\s*=\s*(\d+)", delay_code).group(1))
            return delay_value / 1000
        return None

    def get_base_url(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url

    def save_quotes(self, quotes):
        with jsonlines.open(self.output_file, mode="w") as writer:
            writer.write_all(quotes)

scraper = QuoteScraper()
asyncio.run(scraper.run())
