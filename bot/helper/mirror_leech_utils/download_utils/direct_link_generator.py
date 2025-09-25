from cloudscraper import create_scraper
from hashlib import sha256
from http.cookiejar import MozillaCookieJar
from json import loads
from lxml.etree import HTML
from os import path as ospath
from re import findall, match, search
from requests import Session, post, get
from requests.adapters import HTTPAdapter
from time import sleep
from urllib.parse import parse_qs, urlparse, quote
from urllib3.util.retry import Retry
from uuid import uuid4
from base64 import b64decode, b64encode
import random

from ....core.config_manager import Config
from ...ext_utils.exceptions import DirectDownloadLinkException
from ...ext_utils.help_messages import PASSWORD_ERROR_MESSAGE
from ...ext_utils.links_utils import is_share_link
from ...ext_utils.status_utils import speed_string_to_bytes

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
)

# US proxy list for bypassing geographic restrictions
US_PROXIES = [
    "http://38.154.227.167:5868",
    "http://185.199.229.156:7492",
    "http://185.199.228.220:7300",
    "http://188.74.210.207:6286",
    "http://38.91.107.229:3128",
    "http://8.219.97.248:80",
    "http://23.227.38.66:80",
    "http://154.85.35.235:8888",
]

def get_us_proxy():
    """Get a random US proxy to bypass geographic restrictions"""
    return random.choice(US_PROXIES)

def create_us_session():
    """Create a session with US proxy and proper headers"""
    session = Session()
    proxy = get_us_proxy()
    session.proxies = {"http": proxy, "https": proxy}
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    })
    return session

def direct_link_generator(link):
    """direct links generator"""
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    elif "freshporno.net" in domain:
        return freshporno(link)
    elif "freeporn.gg" in domain:
        return freeporn(link)
    elif "yadi.sk" in link or "disk.yandex." in link:
        return yandex_disk(link)
    elif "buzzheavier.com" in domain:
        return buzzheavier(link)
    # ... rest of your existing domains ...
    else:
        raise DirectDownloadLinkException(f"No Direct link function found for {link}")

def freshporno(url):
    """
    Generate a direct download link for freshporno.net URLs.
    Bypasses anti-leech protection and geographic restrictions.
    """
    try:
        # Use US proxy to bypass geographic restrictions
        session = create_us_session()
        
        # Add referer and other headers to bypass anti-leech
        session.headers.update({
            "Referer": "https://freshporno.net/",
            "Origin": "https://freshporno.net",
            "Sec-Fetch-Site": "same-origin",
        })
        
        # First, try to get the page to establish session
        response = session.get(url.split('?')[0], timeout=30)
        
        if response.status_code == 410:
            # Site might be blocking based on headers, try different approach
            session.headers.update({
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "*/*",
            })
            response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            # Try with different user agent and headers
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                "Accept": "video/mp4,video/webm,video/*;q=0.9,*/*;q=0.8",
            })
            response = session.get(url, timeout=30)
        
        # If still getting errors, try to extract from the main page
        if response.status_code != 200:
            # Get the video page to find alternative links
            video_id = url.split('/')[-2] if '/get_file/' in url else None
            if video_id:
                main_page_url = f"https://freshporno.net/videos/{video_id}/"
                main_response = session.get(main_page_url, timeout=30)
                if main_response.status_code == 200:
                    # Try to find video source in page
                    html = HTML(main_response.text)
                    video_sources = html.xpath('//video/source/@src')
                    if video_sources:
                        return video_sources[0]
        
        # If direct access works, return the URL
        if response.status_code == 200:
            return url
            
        raise DirectDownloadLinkException(f"ERROR: Failed to access freshporno.net (Status: {response.status_code})")
        
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}")

def freeporn(url):
    """
    Generate a direct download link for freeporn.gg URLs.
    Bypasses rate limiting and anti-leech protection.
    """
    try:
        # Use US proxy and rotate user agents
        session = create_us_session()
        
        # Add specific headers for freeporn.gg
        session.headers.update({
            "Referer": "https://www.freeporn.gg/",
            "Origin": "https://www.freeporn.gg",
            "Sec-Fetch-Dest": "video",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
        })
        
        # Add delay to avoid rate limiting
        sleep(random.uniform(2, 5))
        
        # Try direct access first
        response = session.get(url, timeout=30, stream=True)
        
        if response.status_code == 429:
            # Rate limited, wait longer and try with different IP
            sleep(10)
            session = create_us_session()  # Get new session with different proxy
            response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            # Try with mobile headers
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
                "Accept": "video/mp4,video/*;q=0.9,*/*;q=0.8",
            })
            response = session.get(url, timeout=30)
        
        # If still failing, try to find alternative source
        if response.status_code != 200:
            # Extract video ID and try alternative endpoints
            parts = url.split('/')
            if len(parts) >= 7:
                video_id = parts[6]  # 93691738 from the example URL
                # Try different CDN endpoints
                cdn_urls = [
                    url,
                    url.replace('freeporn.gg', 'cdn.freeporn.gg'),
                    url.replace('/get_file/', '/stream/'),
                ]
                
                for cdn_url in cdn_urls:
                    try:
                        test_response = session.head(cdn_url, timeout=10)
                        if test_response.status_code == 200:
                            return cdn_url
                    except:
                        continue
        
        if response.status_code == 200:
            return url
            
        raise DirectDownloadLinkException(f"ERROR: Failed to access freeporn.gg (Status: {response.status_code})")
        
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}")

# ... rest of your existing functions remain the same ...

def get_captcha_token(session, params):
    recaptcha_api = "https://www.google.com/recaptcha/api2"
    res = session.get(f"{recaptcha_api}/anchor", params=params)
    anchor_html = HTML(res.text)
    if not (anchor_token := anchor_html.xpath('//input[@id="recaptcha-token"]/@value')):
        return None
    params["c"] = anchor_token[0]
    params["reason"] = "q"
    res = session.post(f"{recaptcha_api}/reload", params=params)
    if token := findall(r'"rresp","(.*?)"', res.text):
        return token[0]

def buzzheavier(url):
    """
    Generate a direct download link for buzzheavier URLs.
    @param link: URL from buzzheavier
    @return: Direct download link
    """
    pattern = r"^https?://buzzheavier\.com/[a-zA-Z0-9]+$"
    if not match(pattern, url):
        return url

    def _bhscraper(url, folder=False):
        session = Session()
        if "/download" not in url:
            url += "/download"
        url = url.strip()
        session.headers.update(
            {
                "referer": url.split("/download")[0],
                "hx-current-url": url.split("/download")[0],
                "hx-request": "true",
                "priority": "u=1, i",
            }
        )
        try:
            response = session.get(url)
            d_url = response.headers.get("Hx-Redirect")
            if not d_url:
                if not folder:
                    raise DirectDownloadLinkException("ERROR: Gagal mendapatkan data")
                return
            return d_url
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e

    with Session() as session:
        tree = HTML(session.get(url).text)
        if link := tree.xpath(
            "//a[contains(@class, 'link-button') and contains(@class, 'gay-button')]/@hx-get"
        ):
            return _bhscraper(f"https://buzzheavier.com{link[0]}")
        elif folders := tree.xpath("//tbody[@id='tbody']/tr"):
            details = {"contents": [], "title": "", "total_size": 0}
            for data in folders:
                try:
                    filename = data.xpath(".//a")[0].text.strip()
                    _id = data.xpath(".//a")[0].attrib.get("href", "").strip()
                    size = data.xpath(".//td[@class='text-center']/text()")[0].strip()
                    url = _bhscraper(f"https://buzzheavier.com{_id}", True)
                    item = {
                        "path": "",
                        "filename": filename,
                        "url": url,
                    }
                    details["contents"].append(item)
                    size = speed_string_to_bytes(size)
                    details["total_size"] += size
                except:
                    continue
            details["title"] = tree.xpath("//span/text()")[0].strip()
            return details
        else:
            raise DirectDownloadLinkException("ERROR: No download link found")

# ... continue with all your other existing functions ...
