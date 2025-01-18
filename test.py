import requests
from bs4 import BeautifulSoup

# URL of the website to scrape
url = "https://pub.dev/packages/proto_base_client/score"  # Replace with the actual URL

# Send a GET request to the website
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, "html.parser")

# Find the first element with the class 'score-key-figure-value'
downloads_element = soup.find("div", class_="packages-score packages-score-downloads")
downloads_value = downloads_element.find("span", class_="packages-score-value-number").text

print("Number of downloads:", downloads_value)