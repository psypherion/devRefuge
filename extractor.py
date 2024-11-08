import json
import os
import re
import asyncio
from typing import List

class Extractor:
    """
    A class to asynchronously extract links from files and update them into a JSON structure.
    """

    def __init__(self, json_path: str, links_dir: str):
        """
        Initializes the Extractor with paths for the JSON file and links directory.

        Args:
            json_path (str): Path to the JSON file.
            links_dir (str): Path to the directory containing link files.
        """
        self.json_path = json_path
        self.links_dir = links_dir
        self.languages_dict = self.load_json()

    def load_json(self) -> dict:
        """
        Loads the JSON file into a dictionary.

        Returns:
            dict: The content of the JSON file as a dictionary.
        """
        with open(self.json_path, "r") as file:
            return json.load(file)

    def save_json(self) -> None:
        """
        Saves the updated dictionary back to the JSON file.
        """
        with open(self.json_path, "w") as file:
            json.dump(self.languages_dict, file, indent=4)
        print("Updated languages.json saved.")

    async def extract_links(self, filepath: str) -> List[str]:
        """
        Reads a file asynchronously and returns a list of extracted links.

        Args:
            filepath (str): Path to the file.

        Returns:
            list: List of unique links.
        """
        # Use asyncio.to_thread to read the file in a non-blocking way
        content = await asyncio.to_thread(self._read_file, filepath)
        # Extract links with a regex pattern
        links = re.findall(r'\]\(([^)]+)\)', content)
        return links

    def _read_file(self, filepath: str) -> str:
        """Helper method to read a file in a blocking manner."""
        with open(filepath, "r") as file:
            return file.read()

    async def process_file(self, filepath: str) -> None:
        """
        Processes a single file asynchronously to extract links and update the JSON dictionary.

        Args:
            filepath (str): Name of the file to process.
        """
        lang_name = filepath.split(".txt")[0]

        if lang_name in self.languages_dict:
            links = await self.extract_links(filepath=os.path.join(self.links_dir, filepath))
            urls = [
                link if link.startswith("https://") else self.languages_dict[lang_name]["tutorial"] + link
                for link in links
            ]

            # Update the links in the dictionary
            self.languages_dict[lang_name]["links"] = urls
            print(f"Processed {lang_name}: {urls}")

    async def process_links(self) -> None:
        """
        Asynchronously processes all files in the links directory, extracts links, and updates the JSON dictionary.
        """
        filepaths = os.listdir(self.links_dir)
        tasks = [self.process_file(filepath) for filepath in filepaths]
        await asyncio.gather(*tasks)

        # Save the updated dictionary
        self.save_json()

async def main():
    json_path = "languages.json"
    links_dir = "links"
    link_extractor = Extractor(json_path=json_path, links_dir=links_dir)
    await link_extractor.process_links()

if __name__ == "__main__":
    asyncio.run(main())
