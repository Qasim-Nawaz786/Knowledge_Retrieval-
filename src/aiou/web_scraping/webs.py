import openai
from bs4 import BeautifulSoup  # poetry add beautifulsoup4
import requests
import pdfkit   # poetry add pdfkit
import time


def scrape_website():
    response = requests.get("https://aiou.edu.pk/")
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup.get_text())
    # return soup.get_text()


scrape_website()


# def text_to_pdf(text, filename):
#     path_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  # Path to the wkhtmltopdf binary
#     pdfkit.from_string(text, filename, configuration=pdfkit.configuration(
#         wkhtmltopdf=path_wkhtmltopdf))
#     return filename


# def upload_to_openai(filepath):
#     with open(filepath, "rb")as file:
#         print(f'file path{filepath}')
#         response = openai.files.create(file=file.read(), purpose="assistants")
#         print(response.id)
#     return response.id
