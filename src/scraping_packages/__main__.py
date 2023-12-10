# __main__.py

from scraping_packages.spotify_artist_searcher import SpotifyArtistFetcher
from scraping_packages.timeout_restaurant_scraper import TimeoutRestaurantScraper
from scraping_packages.Timeout_Sitemap_Parser import TimeoutSitemapScraper

def main():
    # Instantiate objects of the classes and perform actions
    spotify_artist_fetcher = SpotifyArtistFetcher()
    timeout_restaurant_scraper = TimeoutRestaurantScraper()
    Timeout_Sitemap_Parser = TimeoutSitemapScraper()

    # Example usage of the classes
    # spotify_artist_fetcher.search_artist("Artist Name")
    # timeout_restaurant_scraper.scrape_restaurants("City Name")
    # timeout_sitemap_scraper.parse_sitemap("Sitemap URL")

if __name__ == "__main__":
    main()
