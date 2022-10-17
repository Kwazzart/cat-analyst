import os

TOKEN = '5554474456:AAH59s3E6GIngfY6KJKIqsUue8ON-JO5qa8'

DATA_URL = str(os.getcwd())
DATA_URL = DATA_URL.split("\\")
url = ""
for el_url in DATA_URL:
    if el_url == "cat-analyst":
        break
    url += f'{el_url}\\'
DATA_URL = url[:-1]
