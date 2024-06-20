import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import concurrent.futures
import time

def extract_jobs(soup):
    jobs = []
    for li in soup.select('ul.list > li.list-row'):
        title = li.select_one('h2 a')
        employer = li.select_one('span.employer')
        if title and employer:
            jobs.append({
                'title': title.get_text(strip=True),
                'url': title.get('href', '').strip(),
                'employer': employer.get_text(strip=True)
            })
    return jobs

def get_pagination_urls(base_url, soup):
    return {urljoin(base_url, a['href']) for a in soup.select('ul.pagination li a') if a.get('href')}

def fetch_and_parse(url, session):
    with session.get(url) as response:
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

def process_url(url, session):
    soup = fetch_and_parse(url, session)
    jobs = extract_jobs(soup)
    for page_url in get_pagination_urls(url, soup):
        jobs.extend(extract_jobs(fetch_and_parse(page_url, session)))
    return jobs

def read_urls(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.startswith('http')]

def write_jobs_to_file(directory, position, jobs):
    path = os.path.join(directory, f'{position}_jobs.json')
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(jobs, file, indent=4)
    return path

def create_directory_if_not_exists(path):
    os.makedirs(path, exist_ok=True)

def main():
    start_time = time.time()

    urls_file = 'positionCrunch.txt'
    output_dir = 'ScrappedPositions'
    create_directory_if_not_exists(output_dir)

    urls = read_urls(urls_file)
    with requests.Session() as session:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_url = {executor.submit(process_url, url, session): url for url in urls}

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    jobs = future.result()
                    position_name = url.split('/')[-2]
                    position_directory = os.path.join(output_dir, position_name)
                    create_directory_if_not_exists(position_directory)

                    if jobs:
                        file_path = write_jobs_to_file(position_directory, position_name, jobs)
                        print(f"Saved job details for {position_name} in {file_path}")
                    else:
                        print(f"No jobs found for {position_name}")

                except Exception as e:
                    print(f"Error processing {url}: {e}")

    print(f"Script executed in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
