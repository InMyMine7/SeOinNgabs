import requests
import re
import time
from collections import Counter
from pytrends.request import TrendReq
from datetime import date
from datetime import datetime
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
10. Analisis Kecepatan Muat Gambar di Halaman   
11. Keyword Density Checker Tool
12. .htaccess File Generator Tool
13. Robots.txt Generator Tool
14. Meta Tag Generator
15. Terms Of Services Generator Tool
16. Privacy Policy Generator Tool
17. Disclaimer Generator Tool
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



# Fungsi untuk menganalisis kecepatan muat gambar
def analyze_image_load_speed():
    clear()
    print('===== Analyze Image Load Speed =====')
    
    try:
        url = input("\nMasukkan URL halaman: ").strip()
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                if not img_url.startswith(('http://', 'https://')):
                    img_url = url.rstrip('/') + '/' + img_url.lstrip('/')
                
                start_time = time.time()
                try:
                    img_response = requests.get(img_url, stream=True)
                    load_time = time.time() - start_time
                    print("\n\033[92mGambar di {} memuat dalam waktu {:.2f} detik\033[0m".format(img_url, load_time))
                except requests.RequestException:
                	print("\n\033[92mGagal memuat gambar di {}\033[0m".format(img_url))
    except requests.RequestException as e:
    	print("\033[91mGagal memeriksa kecepatan gambar untuk {}: {}\033[0m".format(url, e))

# Fungsi untuk memeriksa kepadatan kata kunci
def keyword_density_checker():
    clear()
    print('=====Keyword Density Checker=====\n')
    url = input("\nMasukkan URL halaman: ").strip()

    try:
        if not re.match(r'^https?://', url):
            url = 'http://' + url

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            words = re.findall(r'\w+', text.lower())
            word_count = Counter(words)
            
            keyword = input("Masukkan kata kunci yang ingin diperiksa: ").strip().lower()

            if keyword:
                keyword_frequency = word_count[keyword] 
                total_words = sum(word_count.values())

                if total_words > 0:
                    density = (keyword_frequency / total_words) * 100  
                    print(f"\n\033[92mKepadatan kata kunci '{keyword}': {density:.2f}% ({keyword_frequency} kali dari {total_words} kata)\033[0m")
                else:
                    print("\033[91mHalaman tidak mengandung teks.\033[0m")
            else:
                print("\033[91mKata kunci tidak dimasukkan.\033[0m")
        else:
            print("\033[91mPermintaan tidak berhasil.\033[0m")
    
    except requests.exceptions.RequestException as e:
        print("Terjadi kesalahan permintaan:", e)


# Fungsi untuk membuat .htaccess
def generate_htaccess():
    print("\033[92m===== .htaccess File Generator =====\033[0m\n")
    htaccess_content = []

    print("\033[94m1. Redirect HTTP to HTTPS\033[0m")
    redirect_https = input("Do you want to redirect HTTP to HTTPS? (y/n): ").strip().lower()
    if redirect_https == 'y':
        htaccess_content.append("RewriteEngine On")
        htaccess_content.append("RewriteCond %{HTTPS} off")
        htaccess_content.append("RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]")

    print("\033[94m2. Custom 404 Error Page\033[0m")
    custom_404 = input("Do you want to set a custom 404 error page? (y/n): ").strip().lower()
    if custom_404 == 'y':
        error_page = input("Enter the path for the custom 404 error page (e.g., /404.html): ").strip()
        htaccess_content.append(f"ErrorDocument 404 {error_page}")

    print("\033[94m3. Set Cache Control Headers\033[0m")
    cache_control = input("Do you want to set cache control headers for static files? (y/n): ").strip().lower()
    if cache_control == 'y':
        htaccess_content.append("# Cache control for static files")
        htaccess_content.append("<FilesMatch \"\.(jpg|jpeg|png|gif|css|js|woff|woff2|ttf|svg|eot|ico)$\">")
        htaccess_content.append("Header set Cache-Control \"max-age=31536000, public\"")
        htaccess_content.append("</FilesMatch>")

    print("\033[94m4. Disable Directory Listing\033[0m")
    disable_directory_listing = input("Do you want to disable directory listing? (y/n): ").strip().lower()
    if disable_directory_listing == 'y':
        htaccess_content.append("Options -Indexes")

    print("\033[94m5. Enable GZIP Compression\033[0m")
    enable_gzip = input("Do you want to enable GZIP compression? (y/n): ").strip().lower()
    if enable_gzip == 'y':
        htaccess_content.append("# Enable GZIP Compression")
        htaccess_content.append("AddOutputFilterByType DEFLATE text/plain")
        htaccess_content.append("AddOutputFilterByType DEFLATE text/html")
        htaccess_content.append("AddOutputFilterByType DEFLATE text/xml")
        htaccess_content.append("AddOutputFilterByType DEFLATE text/css")
        htaccess_content.append("AddOutputFilterByType DEFLATE application/javascript")
        htaccess_content.append("AddOutputFilterByType DEFLATE application/x-javascript")

    print("\033[94m6. Set Custom Redirects\033[0m")
    add_redirect = input("Do you want to add custom redirects? (y/n): ").strip().lower()
    if add_redirect == 'y':
        while True:
            source_url = input("Enter the source URL (e.g., /old-page): ").strip()
            destination_url = input("Enter the destination URL (e.g., /new-page): ").strip()
            htaccess_content.append(f"Redirect 301 {source_url} {destination_url}")
            another_redirect = input("Do you want to add another redirect? (y/n): ").strip().lower()
            if another_redirect != 'y':
                break

    print("\033[94m7. Prevent Hotlinking\033[0m")
    prevent_hotlinking = input("Do you want to prevent hotlinking of images? (y/n): ").strip().lower()
    if prevent_hotlinking == 'y':
        htaccess_content.append("# Prevent Hotlinking")
        htaccess_content.append("RewriteEngine On")
        htaccess_content.append("RewriteCond %{HTTP_REFERER} !^http://(www\.)?yourdomain.com [NC]")
        htaccess_content.append("RewriteCond %{HTTP_REFERER} !^https://(www\.)?yourdomain.com [NC]")
        htaccess_content.append("RewriteRule \.(jpg|jpeg|png|gif|bmp|tiff|svg)$ - [F]")

    with open('.htaccess', 'w') as file:
        file.write("\n".join(htaccess_content))

    print("\033[92m.htaccess file has been generated and saved.\033[0m")

# Fungsi untuk membuat robots.txt
def generate_robots_txt():
    print("\033[92m===== robots.txt File Generator =====\033[0m\n")
    robots_txt_content = []

    print("\033[94m1. Allow or Disallow All Bots\033[0m")
    allow_all_bots = input("Do you want to allow all bots to crawl the site? (y/n): ").strip().lower()
    if allow_all_bots == 'y':
        robots_txt_content.append("User-agent: *")
        robots_txt_content.append("Disallow:")

    else:
        print("\033[94m2. Disallow Specific Paths\033[0m")
        disallow_paths = input("Do you want to disallow specific paths? (y/n): ").strip().lower()
        if disallow_paths == 'y':
            while True:
                path = input("Enter the path to disallow (e.g., /private/): ").strip()
                robots_txt_content.append(f"User-agent: *")
                robots_txt_content.append(f"Disallow: {path}")
                another_path = input("Do you want to add another path? (y/n): ").strip().lower()
                if another_path != 'y':
                    break

    print("\033[94m3. Allow Specific Bots\033[0m")
    allow_specific_bots = input("Do you want to specify rules for individual bots? (y/n): ").strip().lower()
    if allow_specific_bots == 'y':
        while True:
            bot_name = input("Enter the bot name (e.g., Googlebot): ").strip()
            robots_txt_content.append(f"User-agent: {bot_name}")
            path_to_disallow = input(f"Do you want to disallow any paths for {bot_name}? (y/n): ").strip().lower()
            if path_to_disallow == 'y':
                while True:
                    path = input(f"Enter the path to disallow for {bot_name} (e.g., /private/): ").strip()
                    robots_txt_content.append(f"Disallow: {path}")
                    another_path = input("Do you want to add another path for this bot? (y/n): ").strip().lower()
                    if another_path != 'y':
                        break
            another_bot = input("Do you want to add another bot? (y/n): ").strip().lower()
            if another_bot != 'y':
                break

    print("\033[94m4. Set Crawl Delay\033[0m")
    crawl_delay = input("Do you want to set a crawl delay for all bots? (y/n): ").strip().lower()
    if crawl_delay == 'y':
        delay_time = input("Enter the delay time in seconds (e.g., 10): ").strip()
        robots_txt_content.append(f"Crawl-delay: {delay_time}")

    print("\033[94m5. Add Sitemap Location\033[0m")
    add_sitemap = input("Do you want to add the location of your sitemap? (y/n): ").strip().lower()
    if add_sitemap == 'y':
        sitemap_location = input("Enter the URL of your sitemap (e.g., https://example.com/sitemap.xml): ").strip()
        robots_txt_content.append(f"Sitemap: {sitemap_location}")

    with open('robots.txt', 'w') as file:
        file.write("\n".join(robots_txt_content))

    print("\033[92mrobots.txt file has been generated and saved.\033[0m")

# Fungsi untuk membuat meta tag
def generate_meta_tags():
    print("\033[92m===== Meta Tag Generator =====\033[0m\n")

    title = input("\033[94mEnter the page title (e.g., My Website): \033[0m").strip()

    description = input("\033[94mEnter the page description (e.g., A brief description of the page): \033[0m").strip()

    keywords = input("\033[94mEnter the page keywords (comma separated): \033[0m").strip()

    author = input("\033[94mEnter the author name (e.g., John Doe): \033[0m").strip()

    canonical_url = input("\033[94mEnter the canonical URL of the page (optional): \033[0m").strip()

    og_title = input("\033[94mEnter the Open Graph title (optional): \033[0m").strip()
    og_description = input("\033[94mEnter the Open Graph description (optional): \033[0m").strip()
    og_image = input("\033[94mEnter the Open Graph image URL (optional): \033[0m").strip()

    twitter_card = input("\033[94mEnter Twitter card type (summary, summary_large_image, player, or app): \033[0m").strip()
    twitter_title = input("\033[94mEnter Twitter title (optional): \033[0m").strip()
    twitter_description = input("\033[94mEnter Twitter description (optional): \033[0m").strip()
    twitter_image = input("\033[94mEnter Twitter image URL (optional): \033[0m").strip()

    meta_tags = []
    meta_tags.append(f"<title>{title}</title>")
    meta_tags.append(f'<meta name="description" content="{description}">')
    meta_tags.append(f'<meta name="keywords" content="{keywords}">')
    meta_tags.append(f'<meta name="author" content="{author}">')

    if canonical_url:
        meta_tags.append(f'<link rel="canonical" href="{canonical_url}">')

    if og_title:
        meta_tags.append(f'<meta property="og:title" content="{og_title}">')
    if og_description:
        meta_tags.append(f'<meta property="og:description" content="{og_description}">')
    if og_image:
        meta_tags.append(f'<meta property="og:image" content="{og_image}">')

    if twitter_card:
        meta_tags.append(f'<meta name="twitter:card" content="{twitter_card}">')
    if twitter_title:
        meta_tags.append(f'<meta name="twitter:title" content="{twitter_title}">')
    if twitter_description:
        meta_tags.append(f'<meta name="twitter:description" content="{twitter_description}">')
    if twitter_image:
        meta_tags.append(f'<meta name="twitter:image" content="{twitter_image}">')

    print("\033[92mGenerated Meta Tags:\033[0m\n")
    for tag in meta_tags:
        print(tag)

    with open("meta_tags.html", "w") as file:
        file.write("\n".join(meta_tags))
    print("\033[92mMeta tags have been saved to 'meta_tags.html'.\033[0m")

# Fungsi untuk membuat Terms Of Services
def generate_terms_and_conditions():
    clear()
    print('===== Terms and Conditions Generator =====\n')

    website_name = input("Nama Website: ").strip()
    website_url = input("URL Website: ").strip()
    company_name = input("Nama Perusahaan: ").strip()
    governing_law = input("Hukum yang berlaku (misalnya, 'Indonesia'): ").strip()
    contact_email = input("Email Kontak Perusahaan: ").strip()

    terms_and_conditions_html = f"""
        <h1>Terms and Conditions for {website_name}</h1>

        <p>Welcome to <strong>{website_name}</strong>! These terms and conditions outline the rules and regulations for the use of <a href="{website_url}">{website_url}</a>. By accessing this website, we assume you accept these terms and conditions in full. Do not continue to use {website_name}'s website if you do not accept all of the terms and conditions stated on this page.</p>

        <h2>1. License</h2>
        <p>Unless otherwise stated, {company_name} and/or its licensors own the intellectual property rights for all material on {website_name}. All intellectual property rights are reserved. You may view and/or print pages from {website_url} for your personal use subject to restrictions set in these terms and conditions.</p>

        <h2>2. You Must Not</h2>
        <p>You are specifically restricted from all of the following:</p>
        <ul>
            <li>Publishing any material from {website_url} in any other media</li>
            <li>Selling, sublicensing, and/or otherwise commercializing any website material</li>
            <li>Using this website in any way that is damaging, or that could be damaging, to this website</li>
            <li>Using this website contrary to applicable laws and regulations</li>
        </ul>

        <h2>3. Content Liability</h2>
        <p>We shall not be held responsible for any content that appears on your website. You agree to protect and defend us against all claims that arise on your website.</p>

        <h2>4. Hyperlinking to Our Content</h2>
        <p>The following organizations may link to our website without prior written approval:</p>
        <ul>
            <li>Government agencies</li>
            <li>Search engines</li>
            <li>News organizations</li>
            <li>Online directory distributors</li>
        </ul>

        <h2>5. Governing Law</h2>
        <p>These terms and conditions will be governed by and interpreted in accordance with the laws of {governing_law}, and you submit to the jurisdiction of the courts located in {governing_law} for the resolution of any disputes.</p>

        <h2>6. Modifications to Terms</h2>
        <p>{company_name} reserves the right to revise these terms and conditions at any time. By using this website, you are expected to review these terms regularly.</p>

        <h2>Contact Us</h2>
        <p>If you have any questions about our Terms and Conditions, please contact us at:</p>
        <ul>
            <li>Email: <a href="mailto:{contact_email}">{contact_email}</a></li>
        </ul>

        <p>Last updated: {time.strftime("%Y-%m-%d")}</p>
    
    """

    with open("terms_and_conditions.html", "w") as file:
        file.write(terms_and_conditions_html)

    print("\nTerms and Conditions telah berhasil dibuat dan disimpan sebagai terms_and_conditions.html.")
    

# Fungsi untuk membuat Privacy Policy
def generate_privacy_policy():
    clear()
    print('=====Privacy Policy Generator=====\n')

    website_name = input("Nama Website: ").strip()
    website_url = input("URL Website: ").strip()
    company_name = input("Nama Perusahaan: ").strip()
    company_email = input("Email Kontak Perusahaan: ").strip()
    services = input("Layanan yang disediakan (pisahkan dengan koma): ").strip()
    third_party_services = input("Layanan pihak ketiga yang digunakan (misalnya Google Analytics, Facebook Pixel): ").strip()

    privacy_policy_html = f"""
        <h1>Privacy Policy for {website_name}</h1>

        <p>At <strong>{website_name}</strong> (<a href="{website_url}">{website_url}</a>), accessible from {website_url}, one of our main priorities is the privacy of our visitors. This Privacy Policy document contains types of information that is collected and recorded by {website_name} and how we use it.</p>

        <h2>1. Information We Collect</h2>
        <p>We collect the following information:</p>
        <ul>
            <li>Personal identification information (Name, email address, etc.)</li>
            <li>Non-personal identification information (browser type, device information, etc.)</li>
        </ul>

        <h2>2. How We Use Your Information</h2>
        <p>The information we collect is used for the following purposes:</p>
        <ul>
            <li>To improve our website and services</li>
            <li>To send newsletters or promotional content (if applicable)</li>
            <li>To respond to your inquiries and feedback</li>
        </ul>

        <h2>3. Third-Party Services</h2>
        <p>{website_name} uses third-party services to enhance the user experience. These services include, but are not limited to:</p>
        <ul>
            <li>Google Analytics</li>
            <li>Facebook Pixel</li>
            <li>Other third-party services</li>
        </ul>

        <h2>4. Cookies</h2>
        <p>We use cookies to store non-personal information about our visitors. Cookies help us improve user experience by remembering preferences, and tracking website usage.</p>

        <h2>5. Data Security</h2>
        <p>We take appropriate security measures to protect against unauthorized access, alteration, or destruction of your personal data.</p>

        <h2>6. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
            <li>Access, update, or delete your personal data</li>
            <li>Opt-out of receiving marketing communications at any time</li>
        </ul>

        <h2>7. Changes to This Privacy Policy</h2>
        <p>{website_name} reserves the right to update or change our privacy policy at any time. We encourage you to check this page periodically for any updates.</p>

        <h2>Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us at:</p>
        <ul>
            <li>Email: <a href="mailto:{company_email}">{company_email}</a></li>
            <li>Website: <a href="{website_url}">{website_url}</a></li>
        </ul>

        <p>Last updated: {time.strftime("%Y-%m-%d")}</p>
    
    """

    with open("privacy_policy.html", "w") as file:
        file.write(privacy_policy_html)

    print("\nPrivacy Policy telah berhasil dibuat dan disimpan sebagai privacy_policy.html.")

# Fungsi untuk membuat Disclaimer 
def generate_disclaimer():
    clear()
    print('===== Disclaimer Generator Tool =====\n')

    website_name = input("Nama Website: ").strip()
    website_url = input("URL Website: ").strip()
    company_name = input("Nama Perusahaan: ").strip()
    company_email = input("Email Kontak Perusahaan: ").strip()
    disclaimer_type = input("Jenis Disclaimer (misalnya: 'medical', 'financial', 'website'): ").strip().lower()
    disclaimer_templates = {
        "medical": f"""
            <h1>Medical Disclaimer</h1>
            <p>The information provided by <strong>{website_name}</strong> (<a href="{website_url}">{website_url}</a>) is for general informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.</p>
            <p>If you have any concerns or questions about your health, you should always consult with a physician or other healthcare professional. Do not disregard, avoid, or delay obtaining medical or health-related advice from your healthcare professional because of something you may have read on our website.</p>
        """,
        "financial": f"""
            <h1>Financial Disclaimer</h1>
            <p>All information on this website <strong>{website_name}</strong> (<a href="{website_url}">{website_url}</a>) is published in good faith and for general information purposes only. This website does not offer any financial advice. You should not rely on any information provided on this site to make financial decisions.</p>
            <p>Please consult with a qualified financial advisor before making any investment or financial decisions. <strong>{website_name}</strong> will not be liable for any losses or damages in connection with the use of our website.</p>
        """,
        "website": f"""
            <h1>Website Disclaimer</h1>
            <p>The information provided by <strong>{website_name}</strong> (<a href="{website_url}">{website_url}</a>) is for general informational purposes only. We make no representations or warranties, express or implied, regarding the accuracy, adequacy, or completeness of the information on this site.</p>
            <p>Your use of the website and your reliance on any information on the site is solely at your own risk. <strong>{website_name}</strong> will not be liable for any losses or damages in connection with the use of our website.</p>
        """
    }

    disclaimer_text = disclaimer_templates.get(disclaimer_type, f"""
        <h1>General Disclaimer</h1>
        <p>The information provided by <strong>{website_name}</strong> (<a href="{website_url}">{website_url}</a>) is for general informational purposes only. We make no guarantees about the accuracy or completeness of this information. Your use of the site and any information obtained from it is at your own risk.</p>
        <p>Contact us at <a href="mailto:{company_email}">{company_email}</a> for further inquiries.</p>
    """)

    with open("disclaimer.html", "w") as file:
        file.write(disclaimer_text)

    print("\nDisclaimer telah berhasil dibuat dan disimpan sebagai disclaimer.html.")
 

# Main function to display menu and execute selected option
if __name__ == "__main__":
    clear()
    print(banner_menu)
    choice = input("Choose an option (1-17): ").strip()

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
    elif choice == "10":
    	analyze_image_load_speed()
    elif choice == "11":
    	keyword_density_checker()
    elif choice == "12":
    	generate_htaccess()
    elif choice == "13":
    	generate_robots_txt()
    elif choice == "14":
    	generate_meta_tags()
    elif choice == "15":
    	generate_terms_and_conditions()
    elif choice == "16":
    	generate_privacy_policy()
    elif choice == "17":
    	generate_disclaimer()
    else:
        print("Invalid choice.")
