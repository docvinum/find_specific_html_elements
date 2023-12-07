import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
from multiprocessing import Pool, cpu_count

# Prompt user for input
BASE_URL = input("Enter the base URL of the webpages (e.g., https://example.com/): ")
START = int(input("Enter the starting page number: "))
END = int(input("Enter the ending page number: "))
OUTPUT_FILE = input("Enter the name of the output CSV file (e.g., found_elements.csv): ")
HTML_ELEMENT = input("Enter the HTML element to search for (e.g., div, span): ")
CHUNK_SIZE = (END - START + 1) // cpu_count()

async def fetch(session, url):
    """ Fetch webpage content asynchronously. """
    async with session.get(url) as response:
        return await response.text()

async def process_chunk(start, end):
    """ Process a chunk of webpages to find the HTML element. """
    async with aiohttp.ClientSession() as session:
        for page_id in range(start, end + 1):
            page_url = BASE_URL + str(page_id)
            html_content = await fetch(session, page_url)
            soup = BeautifulSoup(html_content, "html.parser")
            if soup.find_all(HTML_ELEMENT):
                with open(OUTPUT_FILE, "a", newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([page_url])

def worker(start):
    """ Worker function for multiprocessing. """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_chunk(start, start + CHUNK_SIZE))
    loop.close()

if __name__ == "__main__":
    # Write header to the CSV file
    with open(OUTPUT_FILE, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Page URL"])

    # Split the work among multiple processes
    with Pool() as pool:
        pool.map(worker, range(START, END + 1, CHUNK_SIZE))
