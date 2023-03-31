import requests
from bs4 import BeautifulSoup
from warcio.archiveiterator import ArchiveIterator
import wget
import sys
import io

COMMONCRAWL_URL = "https://commoncrawl.s3.amazonaws.com/"

def get_index_files():
    response = requests.get(COMMONCRAWL_URL)
    soup = BeautifulSoup(response.text, "lxml-xml")
    index_files = []
    for link in soup.find_all("Key"):
        href = link.text
        if href.endswith("warc.gz"):
            index_files.append(COMMONCRAWL_URL + href)
    return index_files

def download_pdf_links(pdf_links, output_folder):
    for link in pdf_links:
        try:
            wget.download(link, out=output_folder)
        except Exception as e:
            print(f"Error downloading {link}: {e}")

def process_warc_record(record, pdf_links, limit):
    if record.rec_type == "response":
        url = record.rec_headers.get_header("WARC-Target-URI")
        if url.endswith(".pdf"):
            pdf_links.add(url)
            return len(pdf_links) >= limit
    return False

def scrape_pdfs(index_files, output_folder, limit=None):
    pdf_links = set()
    for index_file in index_files:
        try:
            response = requests.get(index_file, stream=True)
            for record in ArchiveIterator(response.raw, arc2warc=True):
                if process_warc_record(record, pdf_links, limit):
                    break
        except Exception as e:
            print(f"Error processing {index_file}: {e}")

        if limit and len(pdf_links) >= limit:
            break

    download_pdf_links(pdf_links, output_folder)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrape_pdfs.py <output_folder> <pdf_limit>")
        sys.exit(1)

    output_folder = sys.argv[1]
    pdf_limit = int(sys.argv[2])

    index_files = get_index_files()
    scrape_pdfs(index_files, output_folder, pdf_limit)
