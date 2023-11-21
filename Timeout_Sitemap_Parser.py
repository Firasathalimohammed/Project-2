import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


class TimeoutSitemapScraper:
    """
    A class to scrape and organize sitemap URLs from the Timeout website.

    Attributes:
        base_url (str): The URL of the Timeout website for scraping purposes.
        sitemap_records (dict): Stores the URLs from sitemaps and their respective dataframes.
    """

    def __init__(self, base_url):
        """
        Initializes the TimeoutSitemapScraper with the Timeout website URL.
        """
        self.base_url = base_url
        self.sitemap_records = {}
        self.collect_sitemaps()

    def get_web_data(self, url):
        """
        Retrieves content from a specified URL using HTTP GET.
        """
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error during request: {e}")
            return ""

    def extract_sitemap_urls(self, sitemap_url):
        """
        Processes a sitemap URL, extracting all contained URLs and handling nested sitemaps.
        """
        xml_data = self.get_web_data(sitemap_url)
        soup = BeautifulSoup(xml_data, "xml")
        links = []

        for loc in soup.find_all("loc"):
            link = loc.get_text()
            links.append(link)
            if link.endswith(".xml"):
                self.extract_sitemap_urls(link)

        self.sitemap_records[sitemap_url.split("/")[-1]] = pd.DataFrame(
            links, columns=["URLs"]
        )

    def collect_sitemaps(self):
        """
        Collects and processes all sitemaps from the website's robots.txt file.
        """
        robots_txt = self.get_web_data(f"{self.base_url}/robots.txt")
        for line in robots_txt.splitlines():
            if line.startswith("Sitemap:"):
                sitemap_url = line.split(": ")[1].strip()
                self.extract_sitemap_urls(sitemap_url)

    def detail_urls(self):
        """
        Processes and extracts detailed paths from each URL in the sitemaps.
        """
        for key, df in self.sitemap_records.items():
            df["Path_Details"] = df["URLs"].apply(
                lambda x: x.replace("https://www.timeout.com/", "").split("/")
            )

    def store_data_as_csv(self, save_dir="timeout_sitemap_data"):
        """
        Saves sitemap dataframes to CSV files in a specified directory.
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for name, df in self.sitemap_records.items():
            csv_file = f"{save_dir}/{name.split('/')[-1]}.csv"
            df.to_csv(csv_file, index=False)
