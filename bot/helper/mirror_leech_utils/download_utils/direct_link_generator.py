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

# Global proxy list
PROXY_LIST = []
LAST_PROXY_UPDATE = 0
PROXY_UPDATE_INTERVAL = 3600  # 1 hour

def update_proxy_list():
    """Update proxy list from GitHub repository"""
    global PROXY_LIST, LAST_PROXY_UPDATE
    
    current_time = time.time()
    if current_time - LAST_PROXY_UPDATE < PROXY_UPDATE_INTERVAL and PROXY_LIST:
        return
    
    try:
        proxy_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
        response = get(proxy_url, timeout=10)
        if response.status_code == 200:
            proxies = response.text.strip().split('\n')
            # Filter valid proxies and format them properly
            valid_proxies = []
            for proxy in proxies:
                proxy = proxy.strip()
                if proxy and ':' in proxy:
                    # Ensure proper format
                    if not proxy.startswith('http'):
                        proxy = f"http://{proxy}"
                    valid_proxies.append(proxy)
            
            PROXY_LIST = valid_proxies
            LAST_PROXY_UPDATE = current_time
            print(f"Updated proxy list with {len(PROXY_LIST)} proxies")
        else:
            print(f"Failed to fetch proxies: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error updating proxy list: {e}")
        # Fallback to some working proxies if update fails
        if not PROXY_LIST:
            PROXY_LIST = [
                "http://38.154.227.167:5868",
                "http://185.199.229.156:7492",
                "http://185.199.228.220:7300",
                "http://188.74.210.207:6286",
                "http://38.91.107.229:3128",
                "http://8.219.97.248:80",
                "http://23.227.38.66:80",
                "http://154.85.35.235:8888",
            ]

def get_random_proxy():
    """Get a random proxy from the list"""
    update_proxy_list()
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

def create_session_with_retry(max_retries=3, backoff_factor=0.5):
    """Create a session with retry strategy"""
    session = Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    # Mount adapter for both http and https
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def create_proxy_session(max_retries=3):
    """Create a session with proxy and proper headers"""
    session = create_session_with_retry(max_retries)
    
    # Get a random proxy
    proxy_url = get_random_proxy()
    
    if proxy_url:
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        print(f"Using proxy: {proxy_url}")
    
    # Set headers to mimic real browser
    session.headers.update({
        "User-Agent": user_agent,
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

def test_proxy(session, url, timeout=10):
    """Test if the proxy is working"""
    try:
        response = session.head(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

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

def freshporno(url, max_retries=3):
    """
    Generate a direct download link for freshporno.net URLs.
    Bypasses anti-leech protection and geographic restrictions.
    """
    for attempt in range(max_retries):
        try:
            # Create new session for each attempt
            session = create_proxy_session()
            
            # Add referer and other headers to bypass anti-leech
            session.headers.update({
                "Referer": "https://freshporno.net/",
                "Origin": "https://freshporno.net",
                "Sec-Fetch-Site": "same-origin",
            })
            
            print(f"Attempt {attempt + 1} for freshporno.net")
            
            # Test proxy first
            if not test_proxy(session, "https://freshporno.net", 10):
                print("Proxy test failed, trying with new proxy...")
                continue
            
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
                
            print(f"Attempt {attempt + 1} failed with status: {response.status_code}")
            sleep(2)  # Wait before retry
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {str(e)}")
            if attempt < max_retries - 1:
                sleep(2)  # Wait before retry
                continue
    
    # If all attempts fail, try without proxy as last resort
    try:
        print("Trying without proxy...")
        session = create_session_with_retry()
        session.headers.update({
            "User-Agent": user_agent,
            "Referer": "https://freshporno.net/",
        })
        response = session.head(url, timeout=30)
        if response.status_code == 200:
            return url
    except:
        pass
    
    raise DirectDownloadLinkException(f"ERROR: Failed to access freshporno.net after {max_retries} attempts")

def freeporn(url, max_retries=3):
    """
    Generate a direct download link for freeporn.gg URLs.
    Bypasses rate limiting and anti-leech protection.
    """
    for attempt in range(max_retries):
        try:
            # Create new session for each attempt
            session = create_proxy_session()
            
            # Add specific headers for freeporn.gg
            session.headers.update({
                "Referer": "https://www.freeporn.gg/",
                "Origin": "https://www.freeporn.gg",
                "Sec-Fetch-Dest": "video",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
            })
            
            print(f"Attempt {attempt + 1} for freeporn.gg")
            
            # Test proxy first
            if not test_proxy(session, "https://www.freeporn.gg", 10):
                print("Proxy test failed, trying with new proxy...")
                continue
            
            # Add delay to avoid rate limiting
            sleep(random.uniform(2, 5))
            
            # Try direct access first
            response = session.get(url, timeout=30, stream=True)
            
            if response.status_code == 429:
                # Rate limited, wait longer and try with different IP
                sleep(10)
                session = create_proxy_session()  # Get new session with different proxy
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
                
            print(f"Attempt {attempt + 1} failed with status: {response.status_code}")
            sleep(2)  # Wait before retry
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {str(e)}")
            if attempt < max_retries - 1:
                sleep(2)  # Wait before retry
                continue
    
    # If all attempts fail, try without proxy as last resort
    try:
        print("Trying without proxy...")
        session = create_session_with_retry()
        session.headers.update({
            "User-Agent": user_agent,
            "Referer": "https://www.freeporn.gg/",
        })
        response = session.head(url, timeout=30)
        if response.status_code == 200:
            return url
    except:
        pass
    
    raise DirectDownloadLinkException(f"ERROR: Failed to access freeporn.gg after {max_retries} attempts")

# ... rest of your existing functions (buzzheavier, yandex_disk, etc.) remain the same ...

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

# Add this import at the top if not already present
import time

# ... continue with all your other existing functions ...
