import concurrent.futures
import json
import os
import requests
import textwrap
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, base_url="https://www.profesia.sk"):
        self.base_url = base_url

    def scrape_info(self, path):
        full_url = f"{self.base_url}{path}"
        try:
            response = requests.get(full_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            detail_div = soup.find('main', id='detail')
            if detail_div:
                text = detail_div.get_text(separator=' ', strip=True)
                text = re.sub(r'•|\s{2,}', ' ', text)
                return 'Success', self.balanced_line_wrap(text)
            return 'NoDetail', 'Detail section not found'
        except Exception as e:
            return "ScrapingError", str(e)

    @staticmethod
    def balanced_line_wrap(text, width=50):
        return "\n".join(textwrap.wrap(text, width))

class JSONProcessor:
    def __init__(self, root_dir, scraper):
        self.root_dir = root_dir
        self.scraper = scraper
        self.processing_times = []

    def process_json_files(self):
        total_start_time = time.time()
        total_entries, processed_entries = 0, 0

        for subdir, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(subdir, file)
                    data = self.read_json(file_path)
                    total_entries += len(data)

                    processed_data, scraped_data, start_time = self.process_file(file_path, data)
                    processed_entries += len(data)
                    self.write_results(subdir, file, processed_data, scraped_data, start_time)

        self.processing_times.append({"overall_time": time.time() - total_start_time})
        self.write_processing_times()

    def read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def process_file(self, file_path, data):
        start_time = time.time()
        updated_data, scraped_data = [], []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.scraper.scrape_info, item['url']): item for item in data}
            for future in concurrent.futures.as_completed(futures):
                item = futures[future]
                status, info = future.result()
                if status == 'Success':
                    updated_data.append(item)
                    scraped_data.append(f"Title: {item['title']}\nEmployer: {item['employer']}\nURL: {self.scraper.base_url}{item['url']}\nScraped Info:\n{info}\n")
        return updated_data, scraped_data, start_time

    def write_results(self, subdir, file, processed_data, scraped_data, start_time):
        json_path = os.path.join(subdir, file)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=4)

        text_path = os.path.join(subdir, file.replace('.json', '_scraped.txt'))
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("---------\n".join(scraped_data))

        self.log_progress(file, start_time)

    def log_progress(self, file, start_time):
        elapsed_time = time.time() - start_time
        print(f"Completed processing {file} in {elapsed_time:.2f} seconds.")
        self.processing_times.append({"position-name": file, "time": elapsed_time})

    def write_processing_times(self):

        current_dir = os.getcwd()
        process_times_dir = os.path.join(current_dir, '.processTimes')
        os.makedirs(process_times_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_times_file_path = os.path.join(process_times_dir, f"processing_times_{timestamp}.json")
        with open(process_times_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.processing_times, f, indent=4)

scraper = WebScraper()
processor = JSONProcessor('ScrappedPositions', scraper)
processor.process_json_files()