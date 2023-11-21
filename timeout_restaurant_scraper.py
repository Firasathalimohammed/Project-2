import requests
from bs4 import BeautifulSoup
import pandas as pd


class TimeoutRestaurantScraper:
    """
    A scraper for extracting restaurant information from Timeout New York.

    Attributes:
        base_url (str): The base URL for Timeout New York.
    """

    def __init__(self, base_url):
        """
        Initializes the TimeoutRestaurantScraper with a base URL.

        Args:
            base_url (str): The base URL for Timeout New York.
        """
        self.base_url = base_url

    def get_soup(self, url):
        """
        Fetches and parses HTML content from a URL.

        Args:
            url (str): URL to fetch the content from.

        Returns:
            BeautifulSoup: Parsed HTML content of the page.
        """
        response = requests.get(url)
        return BeautifulSoup(response.content, "html.parser")

    def scrape_restaurant_list(self):
        soup = self.get_soup(
            self.base_url + "/newyork/restaurants/100-best-new-york-restaurants"
        )
        all_articles = soup.find_all("article", class_="tile _article_kc5qn_1")
        restaurant_data = [
            self.extract_restaurant_data(article) for article in all_articles
        ]
        return restaurant_data

    def extract_restaurant_data(self, article):
        restaurant_name = article.find("h3").get_text().strip().split(".")[1]
        img_tag, figcaption_tag = article.find("img"), article.find("figcaption")
        image_url, photograph_credit = (
            img_tag["src"] if img_tag else None,
            figcaption_tag.get_text().strip() if figcaption_tag else None,
        )
        summary = " ".join([p.get_text().strip() for p in article.find_all("p")])
        tags = [
            span.get_text().strip()
            for span in article.find_all("span", class_="_text_163gl_28")
        ]
        read_more_link_tag = article.find("a", class_="_a_12eii_1")
        full_read_more_link = (
            self.base_url + read_more_link_tag["href"] if read_more_link_tag else None
        )

        return {
            "Restaurant Name": restaurant_name,
            "Image URL": image_url,
            "Photograph Credit": photograph_credit,
            "Summary": summary,
            "Tags": tags,
            "Read More Link": full_read_more_link,
        }

    def scrape_restaurant_review(self, url):
        soup = self.get_soup(url)
        review_section = soup.find("section", {"data-section-name": "review"})
        return self.extract_review_details(review_section) if review_section else {}

    def extract_review_details(self, review_section):
        timeout_says = review_section.find("p", {"data-testid": "summary_testID"})
        stars = review_section.find_all(
            "span", {"data-testid": "star_testID", "class": "_filled_k40fn_19"}
        )
        content = review_section.find("div", {"data-testid": "annotation_testID"})

        return {
            "Time Out says": timeout_says.get_text().strip() if timeout_says else None,
            "Star Rating": len(stars),
            "Review Content": content.get_text().strip() if content else None,
        }

    def scrape_restaurant_details(self, url):
        soup = self.get_soup(url)
        details_info = soup.find("div", {"data-testid": "details-info_testID"})
        return self.extract_additional_details(details_info) if details_info else {}

    def extract_additional_details(self, details_info):
        address_parts = details_info.find_all("dd", class_="_description_k1wdy_9")[:3]
        address = ", ".join([part.get_text().strip() for part in address_parts])
        contact_info = details_info.find("a", href=lambda href: href and "tel:" in href)
        menu_link = details_info.find("a", href=lambda href: href and "menu" in href)
        opening_hours = details_info.find(
            "dd",
            class_="_description_k1wdy_9",
            string=lambda text: text and ("pm" in text or "am" in text),
        )

        return {
            "Address": address,
            "Contact": contact_info.get_text().strip() if contact_info else None,
            "Menu Link": menu_link["href"] if menu_link else None,
            "Opening Hours": opening_hours.get_text().strip()
            if opening_hours
            else None,
        }

    def combine_data(self):
        restaurant_list = self.scrape_restaurant_list()
        combined_data = []
        for restaurant in restaurant_list:
            read_more_url = restaurant["Read More Link"]
            if read_more_url:
                review_details = self.scrape_restaurant_review(read_more_url)
                additional_details = self.scrape_restaurant_details(read_more_url)
                combined_info = {**restaurant, **review_details, **additional_details}
                combined_data.append(combined_info)

        return pd.DataFrame(combined_data)

    def scrape_and_save(self, output_filename):
        """
        Scrape restaurant data and save it to a CSV file.

        Args:
            output_filename (str): Filename for the output CSV.
        """
        combined_data = self.combine_data()
        self.store_to_csv(combined_data, output_filename)
        return combined_data

    def store_to_csv(self, dataframe, file_name):
        dataframe.to_csv(file_name, index=False)
        print(f"Data saved to {file_name}")
