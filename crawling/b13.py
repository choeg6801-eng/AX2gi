from bs4 import BeautifulSoup 
#pip install beautifulsoup4
import requests
import pandas as pd


response= requests.get("https://www.google.com")

html = response.text 

soup= BeautifulSoup(html, "html.parser")

