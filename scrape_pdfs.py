import requests
import sys
import json
import wget
from urllib.parse import urlencode

CC_CDX_API = "http://index.commoncrawl.org/cdx/search/cdx"

def get_pdf_links(limit):
    params = {
        "url": "*",
        "output": "json",
        "limit": limit,
        "filter": "mime:application/pdf",
        "collapse": "urlkey",
        "showNumPages": "true",
        "fl": "url"
    }
    query_url = CC_CDX_API + "?" + urlencode(params)

    response = requests.get(query_url)
    pdf_links = set()
    for line in response.iter_lines():
        line = line.strip()
        if line:
            try:
                data = json.loads(line)
                pdf_links.add(data)
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

    pdf_links = get_pdf_links(pdf_limit)
    download_pdfs(pdf_links, output_folder)
