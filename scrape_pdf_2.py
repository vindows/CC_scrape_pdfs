import requests
import sys
import json
import wget
from urllib.parse import urlencode

CC_INDEX_API = "https://index.commoncrawl.org/collinfo.json"

def get_latest_cc_index():
    response = requests.get(CC_INDEX_API)
    indexes = response.json()
    latest_index = indexes[0]["id"]
    return latest_index

def get_pdf_links(index, limit):
    query_url = f"https://index.commoncrawl.org/{index}-cc-index?"
    params = {
        "url": "*.pdf",
        "output": "json",
        "limit": limit,
        "filter": "mime:application/pdf"
    }
    query_url += urlencode(params)

    response = requests.get(query_url)
    pdf_links = set()
    for line in response.iter_lines():
        line = line.strip()
        if line:
            try:
                data = json.loads(line)
                pdf_links.add(data["url"])
            except json.JSONDecodeError as e:
                print(f"Skipping line due to JSON decoding error: {e}")
                continue

    return pdf_links

def download_pdfs(pdf_links, output_folder):
    for link in pdf_links:
        try:
            wget.download(link, out=output_folder)
        except Exception as e:
            print(f"Error downloading {link}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrape_pdfs.py <output_folder> <pdf_limit>")
        sys.exit(1)

    output_folder = sys.argv[1]
    pdf_limit = int(sys.argv[2])

    index = get_latest_cc_index()
    pdf_links = get_pdf_links(index, pdf_limit)
    download_pdfs(pdf_links, output_folder)
