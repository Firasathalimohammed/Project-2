import requests
import pandas as pd


class SpotifyArtistFetcher:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.spotify.com/v1"
        self.auth_token = None
        self.token_type = None

    def _make_request(self, method, url, data=None, params=None, headers=None):
        """Generic method for making HTTP requests."""
        try:
            response = requests.request(
                method, url, data=data, params=params, headers=headers
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None

    def authenticate(self):
        """Authenticate with the Spotify API to obtain an access token."""
        token_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = self._make_request("POST", token_url, data=auth_data)
        if response:
            auth_response = response.json()
            self.auth_token = auth_response.get("access_token")
            self.token_type = auth_response.get("token_type")

    def fetch_artists(self, query, limit, offset):
        """Fetch a list of artists based on the search query."""
        search_url = f"{self.base_url}/search"
        search_params = {"q": query, "type": "artist", "limit": limit, "offset": offset}
        headers = {"Authorization": f"{self.token_type} {self.auth_token}"}
        return self._make_request(
            "GET", search_url, params=search_params, headers=headers
        )

    def process_artists_data(self, raw_data):
        """Process raw artist data from Spotify API response."""
        return [
            {
                "artist_name": artist["name"],
                "spotify_id": artist["id"],
                "genres": ", ".join(artist["genres"]),
                "popularity_score": artist["popularity"],
                "followers_count": artist["followers"]["total"],
                "spotify_profile_url": artist["external_urls"]["spotify"],
                "image_url": artist["images"][0]["url"] if artist["images"] else None,
            }
            for artist in raw_data
        ]

    def search_and_collect_artists(self, search_query, max_artists=2000):
        """Search for artists and collect their data up to a specified limit."""
        batch_limit = 50
        batch_offset = 0
        collected_artists = []

        while len(collected_artists) < max_artists:
            response = self.fetch_artists(search_query, batch_limit, batch_offset)
            if response:
                response_data = response.json()
                artists = response_data.get("artists", {}).get("items", [])
                collected_artists.extend(self.process_artists_data(artists))

                if len(artists) < batch_limit:
                    break
                batch_offset += batch_limit
            else:
                print("No more data to fetch or reached the API rate limit.")
                break

        return pd.DataFrame(collected_artists[:max_artists])

    def save_data_to_csv(self, dataframe, filepath):
        """Save artist data to a CSV file."""
        try:
            dataframe.to_csv(filepath, index=False)
            print(f"Data successfully saved to {filepath}")
        except IOError as e:
            print(f"IO Error: {e}")
