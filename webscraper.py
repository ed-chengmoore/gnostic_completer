import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def get_translation_links(main_url):
    response = requests.get(main_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve the main page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    translation_links = {}

    # Find all blockquotes containing links
    blockquotes = soup.find_all('blockquote')
    for blockquote in blockquotes:
        links = blockquote.find_all('a', href=True)
        for link in links:
            href = link['href']
            # some dirty hack to fix the links
            if 'http://www.gnosis.org/' not in href:
                if 'naghamm/' not in href:
                    href = 'http://www.gnosis.org/naghamm/' + href.lstrip('/')
                else:
                    href = 'http://www.gnosis.org/' + href.lstrip('/')
            if href.endswith('.html'):
                # Navigate to the parent <ul> element
                parent_ul = link.find_parent('ul')
                if parent_ul:
                    # Find the previous <li> sibling of the <ul> that contains the <strong> tag
                    previous_li = parent_ul.find_previous_sibling('li')
                    if previous_li:
                        codex_name_tag = previous_li.find('strong')
                        if codex_name_tag:
                            codex_name = codex_name_tag.get_text()
                            if codex_name not in translation_links:
                                translation_links[codex_name] = []
                            if href not in translation_links[codex_name]:
                                translation_links[codex_name].append(href)

    return translation_links

def scrape_blockquote(translation_url, codex_name):
    response = requests.get(translation_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve the translation page. Status code: {response.status_code}")
        return None
    text = ''
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all blockquotes
    blockquotes = soup.find_all('blockquote')
    for blockquote in blockquotes:
        if all(phrase not in blockquote.get_text() for phrase in ['This original translation', 'Archive Note']):
            text += ' ' + blockquote.get_text()
    return text

def main():
    main_url = 'http://www.gnosis.org/naghamm/nhlcodex.html'
    translation_links = get_translation_links(main_url)

    for codex_name, translation_url in translation_links.items():
        full_url = translation_url[0]  # Just using the first translation url for now
        blockquote_text = scrape_blockquote(full_url, codex_name)
        if blockquote_text:
            import os
            # Create the 'corpus' directory if it doesn't exist
            if not os.path.exists('corpus'):
                os.makedirs('corpus')
            # Save the blockquote text to a file with the codex name in the 'corpus' directory
            file_path = os.path.join('corpus', f"{codex_name}.txt")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(blockquote_text)
        else:
            print(f"No blockquote found for {codex_name} at {full_url}")

if __name__ == "__main__":
    main()