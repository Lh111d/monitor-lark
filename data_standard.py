import requests
from bs4 import BeautifulSoup
import json
import time

class WebCrawler:
    def __init__(self, start_urls, search_keywords, max_pages=100):
        self.start_urls = start_urls
        self.search_keywords = search_keywords
        self.max_pages = max_pages
        self.visited_urls = set()
        self.extracted_data = []

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_page(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'
        content = soup.get_text()
        if any(keyword in content for keyword in self.search_keywords):
            self.extracted_data.append({
                'url': url,
                'title': title,
                'content': content
            })
            print(f"Extracted data from {url}")

    def crawl(self):
        for url in self.start_urls:
            if len(self.visited_urls) >= self.max_pages:
                break
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                html = self.fetch_page(url)
                if html:
                    self.parse_page(html, url)
                    # Here you could implement more complex logic to find new URLs to visit
                    time.sleep(1)  # Sleep to avoid overwhelming the server

    def save_data(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_path}")

if __name__ == "__main__":
    start_urls = [
        "https://www.baidu.com/",  # Replace with actual URLs
    ]
    search_keywords = ["热点", "社会事件", "舆情分析"]  # Keywords relevant to hot topics

    crawler = WebCrawler(start_urls, search_keywords)
    crawler.crawl()
    crawler.save_data("extracted_data.json")
