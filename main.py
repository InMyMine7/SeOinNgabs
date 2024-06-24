import requests
import re
from pytrends.request import TrendReq
from datetime import date
from bs4 import BeautifulSoup
import json
import sys
import os

banner_menu = '''                                             
 _____     _____ _     _____         _       
|   __|___|     |_|___|   | |___ ___| |_ ___ 
|__   | -_|  |  | |   | | | | . | .'| . |_ -|
|_____|___|_____|_|_|_|_|___|_  |__,|___|___|
                            |___|        
\033[97m[ \033[92mCoded By \033[92m'/Mine7 \033[97m||\033[92m  github.com/InMyMine7 \033[97m||\033[92m t.me/InMyMineee \033[97m]        

1. Google Trends Scrapper
2. Keyword Research
3. Backlink Generator
4. Check Status Url
5. Check Title, Meta, URL Canonical
6. h1, h2, h3, h4, h5, h6 checker
7. Check backlink internal dan external beserta anchor text
8. Check Broken Links
9. Analisa link 403 dan 301    
'''
# Definisi warna untuk output terminal
COLORS = {
    "h1": "\033[92m",   # Hijau
    "h2": "\033[93m",   # Kuning
    "h3": "\033[94m",   # Biru
    "h4": "\033[95m",   # Magenta
    "h5": "\033[96m",   # Sian
    "h6": "\033[91m",   # Merah
    "reset": "\033[0m"  # Reset warna
}

# Fungsi untuk membersihkan layar terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Fungsi untuk melakukan riset keyword
def keyword_research_tool():
    clear()
    print('=====Keyword Research=====\n')
    text = input('Keyword Research Tool: ')

    response = requests.get(f'http://suggestqueries.google.com/complete/search?output=toolbar&hl=id&q={text}')
    suggestions = re.findall('<suggestion data="(.*?)"/>', response.content.decode('utf-8'))
    for suggestion in suggestions:
        print(suggestion)

# Fungsi untuk mengambil tren pencarian terbaru di Google Trends
def get_trending_searches():
    pytrends = TrendReq(hl='id-ID', tz=360)
    trending_searches_df = pytrends.trending_searches(pn='indonesia')
    trending_searches_list = trending_searches_df[0].tolist()

    today = date.today().strftime("%Y-%m-%d")
    clear()
    print('=====Google Trends Scrapper=====\n')
    result = f"Trending Searches in Indonesia ({today}):\n"
    result += "\n".join([f"{i+1}. {search}" for i, search in enumerate(trending_searches_list)])
    
    return result

# Fungsi untuk menghasilkan backlink
def backlink_generator():
    clear()
    print('=====Backlink Generator=====\n')
    site = input("Nama domain\t: ").strip()

    if not site:
        print("Anda tidak memasukkan nama domain. Keluar.")
        return

    with open("backlink.json", "r") as file:
        data = json.load(file)
        for backlink in data:
            url = backlink['url'].replace("inmymine7", site)
            try:
                status = requests.get(url).status_code
            except requests.RequestException:
                status = "Permintaan gagal"
            
            domain = re.search('http:\/\/.*?\/', url).group(0).replace("/", "").replace("http:", "")
            print(f"~ {site} | Hasil -> {domain} status: {status}")

# Fungsi untuk memeriksa status URL
def check_url_status():
    clear()
    print('=====Check Url Status=====')
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        print(f"\nKode respons halaman adalah: \033[92m{response.status_code}\033[0m")

        if response.history:
            original_url = response.history[0].url
            final_url = response.url
            print(f"\n\033[31mURL asli (sebelum diredirect):\033[0m {original_url}")
            print(f"\033[31mURL redirect:\033[0m {final_url}")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)

# Fungsi untuk memeriksa judul, meta deskripsi, URL kanonik, dan gambar OG
def checktittle():
    clear()
    print('=====Check Title, Meta, URL Canonical=====')
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            title = soup.title.text if soup.title else 'N/A'
            meta_description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else 'N/A'
            url_canonical = soup.find('link', attrs={'rel': 'canonical'})['href'] if soup.find('link', attrs={'rel': 'canonical'}) else 'N/A'
            image_og = soup.find('meta', attrs={'property': 'og:image'})['content'] if soup.find('meta', attrs={'property': 'og:image'}) else 'N/A'
            
            print(f"\n\033[31mJudul:\033[0m {title}")
            print(f"\033[31mMeta Deskripsi:\033[0m {meta_description}")
            print(f"\033[31mURL Canonical:\033[0m {url_canonical}")
            print(f"\033[31mGambar OG:\033[0m {image_og}")
        else:
            print("Permintaan tidak berhasil.")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)

# Fungsi untuk memeriksa tag heading (h1, h2, h3, h4, h5, h6)
def check_head():
    clear()
    print('=====h1, h2, h3, h4, h5, h6 checker=====')
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                heading_type = heading.name
                color = COLORS.get(heading_type, COLORS["reset"])
                print(f"{color}{heading_type}: {heading.text}{COLORS['reset']}")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)

# Fungsi untuk menganalisis backlink internal dan eksternal beserta teks jangkar (anchor text)
def analyze_backlinks():
    clear()
    print('=====Check backlink internal dan external beserta anchor text=====')
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            internal_links = []
            external_links = []

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                anchor_text = a_tag.text.strip()

                if re.match(r'^https?://', href):
                    if re.match(r'https?://(www\.)?' + re.escape(url.split('/')[2]), href):
                        internal_links.append((href, anchor_text))
                    else:
                        external_links.append((href, anchor_text))
                elif re.match(r'^/', href):
                    internal_links.append((url.rstrip('/') + href, anchor_text))

            print("\n\033[32mBacklink Internal:\033[0m")
            for link, text in internal_links:
                print(f"{text} -> {link}")

            print("\n\033[32mBacklink Eksternal:\033[0m")
            for link, text in external_links:
                print(f"{text} -> {link}")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)

# Fungsi untuk memeriksa tautan yang rusak (broken links)
def check_broken_links():
    clear()
    print('=====Check Broken Links=====')
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        print("Tunggu sebentar proses ini memakan waktu cukup lama")
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            broken_links = []

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if re.match(r'^https?://', href) or re.match(r'^/', href):
                    try:
                        link_response = requests.head(href, allow_redirects=True)
                        if link_response.status_code >= 400:
                            broken_links.append(href)
                    except requests.exceptions.RequestException:
                        broken_links.append(href)

            if broken_links:
                print("\n\033[91mTautan yang rusak ditemukan:\033[0m")
                for link in broken_links:
                    print(link)
            else:
                print("\n\033[92mTidak ada tautan yang rusak ditemukan.\033[0m")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)

# Fungsi untuk menganalisis tautan dengan kode status 404 dan 301
def analyze_404_301_links():
    clear()
    print('=====Analisa link 403 dan 301=====')
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        print("Tunggu sebentar proses ini memakan waktu cukup lama")
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            links_404 = []
            links_301 = []

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if re.match(r'^https?://', href) or re.match(r'^/', href):
                    try:
                        link_response = requests.head(href, allow_redirects=True)
                        if link_response.status_code == 404:
                            links_404.append(href)
                        elif link_response.status_code == 301:
                            links_301.append(href)
                    except requests.exceptions.RequestException:
                        pass

            if links_404:
                print("\n\033[91mTautan internal dengan kode 404 ditemukan:\033[0m")
                for link in links_404:
                    print(link)
            else:
                print("\n\033[92mTidak ada tautan internal dengan kode 404 ditemukan.\033[0m")

            if links_301:
                print("\n\033[91mTautan internal dengan kode 301 ditemukan:\033[0m")
                for link in links_301:
                    print(link)
            else:
                print("\n\033[92mTidak ada tautan internal dengan kode 301 ditemukan.\033[0m")

    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)

# Main function to display menu and execute selected option
if __name__ == "__main__":
    clear()
    print(banner_menu)
    choice = input("Choose an option (1-9): ").strip()

    if choice == "1":
        print(get_trending_searches())
    elif choice == "2":
        keyword_research_tool()
    elif choice == "3":
        backlink_generator()
    elif choice == "4":
        check_url_status()
    elif choice == "5":
        checktittle()
    elif choice == "6":
        check_head()
    elif choice == "7":
        analyze_backlinks()
    elif choice == "8":
        check_broken_links()
    elif choice == "9":
        analyze_404_301_links()
    else:
        print("Invalid choice.")
