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

def load_proxies():
    """Load proxies from the provided URL"""
    global PROXY_LIST
    try:
        response = get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", timeout=10)
        if response.status_code == 200:
            PROXY_LIST = [line.strip() for line in response.text.split('\n') if line.strip()]
    except:
        pass

def get_random_proxy():
    """Get a random proxy from the list"""
    if not PROXY_LIST:
        load_proxies()
    return random.choice(PROXY_LIST) if PROXY_LIST else None

def create_session_with_proxy():
    """Create a session with random proxy and anti-bot headers"""
    session = create_scraper()
    proxy = get_random_proxy()
    
    if proxy:
        session.proxies = {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }
    
    # Add random headers to avoid detection
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
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
    elif "devuploads" in domain:
        return devuploads(link)
    elif "lulacloud.com" in domain:
        return lulacloud(link)
    elif "uploadhaven" in domain:
        return uploadhaven(link)
    elif "fuckingfast.co" in domain:
        return fuckingfast_dl(link)
    elif "mediafile.cc" in domain:
        return mediafile(link)
    elif "mediafire.com" in domain:
        return mediafire(link)
    elif "osdn.net" in domain:
        return osdn(link)
    elif "github.com" in domain:
        return github(link)
    elif "hxfile.co" in domain:
        return hxfile(link)
    elif "1drv.ms" in link:
        return onedrive(link)
    elif any(x in domain for x in ["pixeldrain.com", "pixeldra.in"]):
        return pixeldrain(link)
    elif "racaty" in domain:
        return racaty(link)
    elif "1fichier.com" in domain:
        return fichier(link)
    elif "solidfiles.com" in domain:
        return solidfiles(link)
    elif "krakenfiles.com" in domain:
        return krakenfiles(link)
    elif "upload.ee" in domain:
        return uploadee(link)
    elif "gofile.io" in domain:
        return gofile(link)
    elif "send.cm" in domain:
        return send_cm(link)
    elif "tmpsend.com" in domain:
        return tmpsend(link)
    elif "easyupload.io" in domain:
        return easyupload(link)
    elif "streamvid.net" in domain:
        return streamvid(link)
    elif "shrdsk.me" in domain:
        return shrdsk(link)
    elif "u.pcloud.link" in domain:
        return pcloud(link)
    elif "qiwi.gg" in domain:
        return qiwi(link)
    elif "mp4upload.com" in domain:
        return mp4upload(link)
    elif "berkasdrive.com" in domain:
        return berkasdrive(link)
    elif "swisstransfer.com" in domain:
        return swisstransfer(link)
    elif any(x in domain for x in ["akmfiles.com", "akmfls.xyz"]):
        return akmfiles(link)
    elif any(
        x in domain
        for x in [
            "dood.watch",
            "doodstream.com",
            "dood.to",
            "dood.so",
            "dood.cx",
            "dood.la",
            "dood.ws",
            "dood.sh",
            "doodstream.co",
            "dood.pm",
            "dood.wf",
            "dood.re",
            "dood.video",
            "dooood.com",
            "dood.yt",
            "doods.yt",
            "dood.stream",
            "doods.pro",
            "ds2play.com",
            "d0o0d.com",
            "ds2video.com",
            "do0od.com",
            "d000d.com",
        ]
    ):
        return doods(link)
    elif any(
        x in domain
        for x in [
            "streamtape.com",
            "streamtape.co",
            "streamtape.cc",
            "streamtape.to",
            "streamtape.net",
            "streamta.pe",
            "streamtape.xyz",
        ]
    ):
        return streamtape(link)
    elif any(x in domain for x in ["wetransfer.com", "we.tl"]):
        return wetransfer(link)
    elif any(
        x in domain
        for x in [
            "terabox.com",
            "nephobox.com",
            "4funbox.com",
            "mirrobox.com",
            "momerybox.com",
            "teraboxapp.com",
            "1024tera.com",
            "terabox.app",
            "gibibox.com",
            "goaibox.com",
            "terasharelink.com",
            "teraboxlink.com",
            "freeterabox.com",
            "1024terabox.com",
            "teraboxshare.com",
            "terafileshare.com",
            "terabox.club",
        ]
    ):
        return terabox(link)
    elif any(
        x in domain
        for x in [
            "filelions.co",
            "filelions.site",
            "filelions.live",
            "filelions.to",
            "mycloudz.cc",
            "cabecabean.lol",
            "filelions.online",
            "embedwish.com",
            "kitabmarkaz.xyz",
            "wishfast.top",
            "streamwish.to",
            "kissmovies.net",
        ]
    ):
        return filelions_and_streamwish(link)
    elif any(x in domain for x in ["streamhub.ink", "streamhub.to"]):
        return streamhub(link)
    elif any(
        x in domain
        for x in [
            "linkbox.to",
            "lbx.to",
            "teltobx.net",
            "telbx.net",
            "linkbox.cloud",
        ]
    ):
        return linkBox(link)
    elif is_share_link(link):
        return filepress(link) if "filepress" in domain else sharer_scraper(link)
    elif any(
        x in domain
        for x in [
            "anonfiles.com",
            "zippyshare.com",
            "letsupload.io",
            "hotfile.io",
            "bayfiles.com",
            "megaupload.nz",
            "letsupload.cc",
            "filechan.org",
            "myfile.is",
            "vshare.is",
            "rapidshare.nu",
            "lolabits.se",
            "openload.cc",
            "share-online.is",
            "upvid.cc",
            "uptobox.com",
            "uptobox.fr",
        ]
    ):
        raise DirectDownloadLinkException(f"ERROR: R.I.P {domain}")
    else:
        raise DirectDownloadLinkException(f"No Direct link function found for {link}")

def freshporno(url):
    """
    Generate a direct download link for freshporno.net URLs.
    Bypasses: Age verification, anti-leech protection, geographic restrictions
    """
    try:
        session = create_session_with_proxy()
        
        # First request to get cookies and bypass initial protection
        session.get("https://freshporno.net/", timeout=10)
        sleep(2)
        
        # Add adult site specific headers
        session.headers.update({
            'Referer': 'https://freshporno.net/',
            'Origin': 'https://freshporno.net',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        # Bypass age verification by setting consent cookie
        session.cookies.set('age_verified', '1', domain='freshporno.net')
        session.cookies.set('adult', 'true', domain='freshporno.net')
        
        # Get the video page to extract tokens
        if '/get_file/' not in url:
            # Extract file ID from URL if it's a page URL
            file_id = url.split('/')[-1].split('.')[0]
            url = f"https://freshporno.net/get_file/1/{file_id}/"
        
        response = session.get(url, timeout=30)
        
        if response.status_code == 410:
            # Try with different approaches for 410 error
            # Method 1: Try with different user agent
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
            })
            response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            # Method 2: Try direct download pattern
            if '/get_file/' in url:
                # Extract parameters from URL
                parts = url.split('/')
                if len(parts) >= 8:
                    file_hash = parts[4]
                    file_id = parts[6]
                    quality = parts[7].split('_')[1] if '_' in parts[7] else '720p'
                    
                    # Construct direct download URL
                    direct_url = f"https://freshporno.net/get_file/2/{file_hash}/25000/{file_id}/{file_id}_{quality}.mp4/?download=true"
                    
                    # Verify the link works
                    verify_response = session.head(direct_url, timeout=10, allow_redirects=True)
                    if verify_response.status_code == 200:
                        return direct_url
        
        # Parse HTML for download links
        html = HTML(response.text)
        
        # Look for download buttons or links
        download_links = html.xpath('//a[contains(@href, "download=true")]/@href')
        if download_links:
            for link in download_links:
                if link.startswith('/'):
                    link = f"https://freshporno.net{link}"
                # Verify the link
                verify_response = session.head(link, timeout=10, allow_redirects=True)
                if verify_response.status_code == 200:
                    return link
        
        # Look for video sources
        video_sources = html.xpath('//video/source/@src')
        if video_sources:
            for src in video_sources:
                if src.startswith('/'):
                    src = f"https://freshporno.net{src}"
                return src
        
        # If no direct link found, try to extract from JavaScript
        scripts = html.xpath('//script/text()')
        for script in scripts:
            if 'download' in script and 'mp4' in script:
                # Extract URLs from JavaScript
                urls = findall(r'https?://[^\s"\']+\.mp4[^\s"\']*', script)
                if urls:
                    return urls[0]
        
        raise DirectDownloadLinkException("ERROR: Unable to extract download link from freshporno.net")
        
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}")

def freeporn(url):
    """
    Generate a direct download link for freeporn.gg URLs.
    Bypasses: Age verification, anti-leech protection, rate limiting (429)
    """
    try:
        session = create_session_with_proxy()
        
        # Add specific headers for freeporn.gg
        session.headers.update({
            'Referer': 'https://www.freeporn.gg/',
            'Origin': 'https://www.freeporn.gg',
            'Accept': '*/*',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        # Set age verification cookies
        session.cookies.set('over18', '1', domain='freeporn.gg')
        session.cookies.set('adult', 'true', domain='freeporn.gg')
        
        # If it's already a direct download link, return it
        if '/get_file/' in url and 'download=true' in url:
            # Verify the link works
            response = session.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return url
        
        # Handle rate limiting (429) with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=30)
                
                if response.status_code == 429:
                    # Rate limited - wait and retry with different proxy
                    sleep_time = (attempt + 1) * 10
                    sleep(sleep_time)
                    session = create_session_with_proxy()  # New session with new proxy
                    continue
                
                if response.status_code != 200:
                    raise DirectDownloadLinkException(f"HTTP Error {response.status_code}")
                
                break
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                sleep((attempt + 1) * 5)
                session = create_session_with_proxy()
        
        html = HTML(response.text)
        
        # Look for direct download links
        download_links = html.xpath('//a[contains(@href, "download=true")]/@href')
        if download_links:
            for link in download_links:
                if link.startswith('/'):
                    link = f"https://www.freeporn.gg{link}"
                return link
        
        # Look for video elements
        video_sources = html.xpath('//video/source/@src')
        if video_sources:
            for src in video_sources:
                if src.startswith('/'):
                    src = f"https://www.freeporn.gg{src}"
                return src
        
        # Extract from JavaScript variables
        scripts = html.xpath('//script/text()')
        for script in scripts:
            # Look for video URLs in JavaScript
            video_patterns = [
                r'videoUrl\s*[=:]\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
                r'src\s*[=:]\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
                r'file\s*[=:]\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
                r'https?://[^\s"\']+\.mp4[^\s"\']*'
            ]
            
            for pattern in video_patterns:
                matches = findall(pattern, script)
                if matches:
                    for match_url in matches:
                        if 'freeporn.gg' in match_url:
                            return match_url
        
        # Try to construct direct download URL from path
        if '/get_file/' in url:
            parts = url.split('/')
            if len(parts) >= 8:
                file_hash = parts[5]
                file_id = parts[7]
                quality = parts[8].split('_')[1] if '_' in parts[8] else '720m'
                
                direct_url = f"https://www.freeporn.gg/get_file/8512/{file_hash}/93691000/{file_id}/{file_id}_{quality}.mp4/?download=true"
                return direct_url
        
        raise DirectDownloadLinkException("ERROR: Unable to extract download link from freeporn.gg")
        
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}")

# [Keep all the existing functions exactly as they were...]
# The rest of your existing functions remain unchanged

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

# [Continue with all your existing functions exactly as they were in the original file...]
# ... (all the rest of your existing functions remain completely unchanged)
