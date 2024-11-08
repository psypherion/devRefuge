import asyncio
import json
import os
import re
import warnings
from typing import Any, List, Dict

from crawl4ai import AsyncWebCrawler, CrawlResult
import logging
logging.basicConfig(level=logging.DEBUG)
warnings.filterwarnings("ignore")


class TutorialScraper:
    """Class to scrape and save tutorial content for different programming languages."""

    def __init__(self, json_path: str, output_dir: str):
        """
        Initializes the scraper with the path to JSON containing URLs
        and the output directory to save scraped content.

        Args:
            json_path (str): Path to the JSON file with language URLs.
            output_dir (str): Directory where content will be saved.
        """
        self.json_path = json_path
        self.output_dir = output_dir
        self.languages = self.load_language_data()

    def load_language_data(self) -> Dict[str, Dict[str, str]]:
        """Loads language data from JSON file."""
        with open(self.json_path, "r") as file:
            return json.load(file)

    async def scrape_content(self, url: str) -> Any:
        """
        Asynchronously scrapes content from a given URL.

        Args:
            url (str): The URL to scrape.

        Returns:
            Any: The result object containing scraped content.
        """
        async with AsyncWebCrawler(verbose=True) as crawler:
            result: CrawlResult = await crawler.arun(url=url)
            return result

    async def save_content(self, key: str, content: Any) -> None:
        """
        Saves scraped content to a text file named after the language key.

        Args:
            key (str): The language key to name the file.
            content (Any): The scraped content to save.
        """
        file_path: str = os.path.join(self.output_dir, f"{key}.txt")
        with open(file_path, "w") as file:
            file.write(content.markdown)
        print(f"Content saved to {file_path}")

    async def scrape_and_save_tutorials(self) -> None:
        """Scrapes and saves content for each language URL in JSON."""
        os.makedirs(self.output_dir, exist_ok=True)
        tasks: List[asyncio.Task] = []

        for key, data in self.languages.items():
            url: str = data.get("tutorial")
            if url:
                tasks.append(self.scrape_and_save(key, url))

        await asyncio.gather(*tasks)

    async def scrape_and_save(self, key: str, url: str) -> None:
        """Helper function to scrape and save content for a specific URL."""
        content: Any = await self.scrape_content(url)
        print(f"Content scraped for {key}")
        await self.save_content(key, content)



class ContentScraper:
    def __init__(self, json_path: str, db_dir: str, max_concurrent_tasks: int = 5):
        """
        Initializes the content scraper with parameters.

        Args:
            json_path (str): Path to the JSON file with language URLs.
            db_dir (str): Directory where the scraped content will be saved.
            max_concurrent_tasks (int): Maximum number of concurrent scraping tasks.
        """
        self.json_path = json_path
        self.db_dir = db_dir
        self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)  # Semaphore for limiting concurrency
        self.languages = self.load_language_data()

    def load_language_data(self) -> Dict[str, Dict[str, str]]:
        """Loads language data from JSON file."""
        with open(self.json_path, "r") as file:
            return json.load(file)

    async def scrape_content(self, url: str) -> Any:
        """
        Asynchronously scrapes content from the given URL.

        Args:
            url (str): URL to scrape.

        Returns:
            Any: The result object containing scraped content.
        """
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result: CrawlResult = await crawler.arun(url=url)
                logging.debug(f"Scraped content from {url}")
                return result
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return None  # Return None if there is an error

    async def save_content(self, lang_key: str, url: str, content: Any) -> None:
        """
        Saves the scraped content to a file in the specified directory.

        Args:
            lang_key (str): Language key for naming the file.
            url (str): The URL used to name the file.
            content (Any): The scraped content to save.
        """
        if content:
            # Create language-specific directory
            lang_dir = os.path.join(self.db_dir, lang_key)
            os.makedirs(lang_dir, exist_ok=True)

            # Use the URL to generate a filename (strip out any special characters)
            filename = url.split("/")[-1].replace(".html", "").replace(":", "_") + ".txt"
            file_path = os.path.join(lang_dir, filename)

            with open(file_path, "w") as file:
                file.write(content.markdown)  # Assuming the content object has a `markdown` attribute

            logging.debug(f"Content saved for {lang_key} to {file_path}")
        else:
            logging.warning(f"No content to save for {url}")

    async def scrape_and_save(self, lang_key: str, url: str) -> None:
        """
        Scrapes content and saves it for the given language and URL.

        Args:
            lang_key (str): Language key for identifying the language.
            url (str): The URL to scrape.
        """
        async with self.semaphore:
            content = await self.scrape_content(url)
            await self.save_content(lang_key, url, content)

    async def scrape_and_save_links(self) -> None:
        """
        Scrapes and saves content for each URL in the `links` field of the languages JSON.
        """
        tasks = []
        for lang_key, data in self.languages.items():
            links = data.get("links", [])
            for url in links:
                tasks.append(self.scrape_and_save(lang_key, url))

        # Limit the number of concurrent tasks by using a semaphore
        await asyncio.gather(*tasks)

    async def run(self) -> None:
        """Starts the content scraping process."""
        os.makedirs(self.db_dir, exist_ok=True)
        await self.scrape_and_save_links()


# Main function to start the scraper
async def main() -> None:
    json_path = "languages.json"
    db_dir = os.path.join(os.path.dirname(__file__), "db")  # Directory where content will be saved

    scraper = ContentScraper(json_path=json_path, db_dir=db_dir)
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
