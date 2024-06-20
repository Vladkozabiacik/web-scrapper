import requests
from bs4 import BeautifulSoup

url = 'https://www.profesia.sk/praca/zoznam-pozicii/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Failed to retrieve the webpage: Status code {response.status_code}")
    exit()

soup = BeautifulSoup(response.content, 'html.parser')

cards = soup.find_all('div', class_='card')
with open('positionCrunch.txt', 'w', encoding='utf-8') as file:
    for card in cards:
        list_items = card.find_all('li')
        for li in list_items:
            a_tag = li.find('a', class_='text-link')
            if a_tag and a_tag.has_attr('href'):
                name = a_tag.get_text(strip=True)
                file.write(f"{name}\nhttps://www.profesia.sk{a_tag['href']}\n\n")

print("Job positions saved to positionCrunch.txt")
