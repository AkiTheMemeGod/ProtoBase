import requests
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError, RequestException

def pub_dev_downloads():
    url = "https://pub.dev/packages/proto_base_client/score"
    scraper_api_url = f"https://scrapenest.pythonanywhere.com/scrape?url={url}"
    try:
        response = requests.get(scraper_api_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        downloads_element = soup.find("div", class_="packages-score packages-score-downloads")
        downloads_value = downloads_element.find("span", class_="packages-score-value-number").text
        return downloads_value
    except ProxyError as e:
        print(f"ProxyError: {e}")
        return "N/A"  # Return a default value or handle accordingly
    except RequestException as e:
        print(f"RequestException: {e}")
        return "N/A"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "N/A"