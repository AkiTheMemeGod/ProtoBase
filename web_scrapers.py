import requests
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError

def pub_dev_downloads():
    url = "https://pub.dev/packages/proto_base_client/score"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        downloads_element = soup.find("div", class_="packages-score packages-score-downloads")
        downloads_value = downloads_element.find("span", class_="packages-score-value-number").text
        return downloads_value
    except ProxyError as e:
        # Log the error or handle it as needed
        print(f"ProxyError: {e}")
        return "N/A"  # Return a default value or handle accordingly