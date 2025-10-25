import requests, re
from bs4 import BeautifulSoup

def immi_homefair_sitemap(link):
    # "https://immi.homeaffairs.gov.au"
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    original_urls=[]
    for script in scripts:
        if script.string: # script.string是beautfulsoup的一个用法，用于获取 script 标签内的文本内容
            matches = re.findall(r'"absolutefriendlyurl":"([^"]+)"', script.string)
            if matches:
                original_urls.extend(matches)
    # urls=[]
    with open('immi_homefair_sitemap.txt','w') as f:
        for url in original_urls:
            url = url.replace("immiauthor.homeaffairs.gov.au", "immi.homeaffairs.gov.au")
            
            f.write(f"{url}\n")
        # urls.append(url)
    print(f"immi_homefair_sitemap.txt generated")
    # return urls

# immi_homefair_sitemap("https://immi.homeaffairs.gov.au")

def wa_sitemap(link):
    sitemap_html = requests.get(link).text
    soup = BeautifulSoup(sitemap_html, 'html.parser')
    links = soup.find_all('a')

    site_links =[]
    for link in links:
        href = link.get("href")
        if (href is not None) and ( href != "/") and (not href.startswith(("http","https","#"))): 
            add_domin = "https://migration.wa.gov.au"+href
            site_links.append(add_domin)
    return site_links

def get_all_wa_links(link1, link2):
    site_links = wa_sitemap(link1)
    home_links = wa_sitemap(link2)
    
    site_links.extend(home_links)
    unique_links = list(set(site_links))
    
    with open('wa_sitemap.txt','w') as f:
        for url in unique_links:
            f.write(f"{url}\n")
        # urls.append(url)
    print(f"wa_sitemap.txt generated")

get_all_wa_links("https://migration.wa.gov.au/sitemap","https://migration.wa.gov.au/")