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

from ....core.config_manager import Config
from ...ext_utils.exceptions import DirectDownloadLinkException
from ...ext_utils.help_messages import PASSWORD_ERROR_MESSAGE
from ...ext_utils.links_utils import is_share_link
from ...ext_utils.status_utils import speed_string_to_bytes

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
)


def direct_link_generator(link):
    """direct links generator"""
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
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
    elif "1drv.ms" in domain:
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
    elif "fullporner.org" in domain:
        return fullporner(link)
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


def fullporner(url):
    """
    FullPorner.org direct download link generator
    Bypasses popup ads and extracts video URL
    """
    with create_scraper() as session:
        try:
            # First request to get the page content
            headers = {
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
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            html = HTML(response.text)
            
            # Try multiple methods to extract video URL
            video_url = None
            
            # Method 1: Look for video source tags
            video_sources = html.xpath('//video/source/@src')
            if video_sources:
                video_url = video_sources[0]
            
            # Method 2: Look for iframe sources
            if not video_url:
                iframe_src = html.xpath('//iframe[@allowfullscreen]/@src')
                if iframe_src:
                    iframe_url = iframe_src[0]
                    if iframe_url.startswith('//'):
                        iframe_url = 'https:' + iframe_url
                    
                    # Follow the iframe
                    iframe_response = session.get(iframe_url, headers=headers, timeout=30)
                    iframe_html = HTML(iframe_response.text)
                    
                    # Look for video sources in iframe
                    iframe_video_sources = iframe_html.xpath('//video/source/@src')
                    if iframe_video_sources:
                        video_url = iframe_video_sources[0]
            
            # Method 3: Look for data-video attributes
            if not video_url:
                data_video = html.xpath('//div[@data-video]/@data-video')
                if data_video:
                    video_url = data_video[0]
            
            # Method 4: Look for JavaScript variables containing video URLs
            if not video_url:
                script_tags = html.xpath('//script[contains(text(), "video")]/text()')
                for script in script_tags:
                    # Look for various video URL patterns
                    patterns = [
                        r'src\s*:\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
                        r'videoUrl\s*=\s*["\'](https?://[^"\']+)["\']',
                        r'file\s*:\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']',
                        r'video_url\s*=\s*["\'](https?://[^"\']+)["\']',
                        r'source\s*:\s*["\'](https?://[^"\']+\.mp4[^"\']*)["\']'
                    ]
                    
                    for pattern in patterns:
                        matches = findall(pattern, script)
                        if matches:
                            video_url = matches[0]
                            break
                    if video_url:
                        break
            
            # Method 5: Look for embed codes with video URLs
            if not video_url:
                embed_scripts = html.xpath('//script[contains(text(), "embed")]/text()')
                for script in embed_scripts:
                    url_patterns = [
                        r'https?://[^\s"\']+\.mp4[^\s"\']*',
                        r'https?://[^\s"\']+\.m3u8[^\s"\']*',
                        r'https?://[^\s"\']+\.webm[^\s"\']*'
                    ]
                    for pattern in url_patterns:
                        matches = findall(pattern, script)
                        if matches:
                            video_url = matches[0]
                            break
                    if video_url:
                        break
            
            if video_url:
                # Clean up the URL
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                
                # Add referer header for the download
                headers = [f"Referer: {url}"]
                return video_url, headers
            else:
                raise DirectDownloadLinkException("ERROR: No video URL found on the page")
                
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__} - {str(e)}")


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


def fuckingfast_dl(url):
    """
    Generate a direct download link for fuckingfast.co URLs.
    @param url: URL from fuckingfast.co
    @return: Direct download link
    """
    url = url.strip()

    try:
        response = get(url)
        content = response.text
        pattern = r'window\.open\((["\'])(https://fuckingfast\.co/dl/[^"\']+)\1'
        if match := search(pattern, content):
            return match.group(2)
        else:
            raise DirectDownloadLinkException(
                "ERROR: Could not find download link in page"
            )

    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def lulacloud(url):
    """
    Generate a direct download link for www.lulacloud.com URLs.
    @param url: URL from www.lulacloud.com
    @return: Direct download link
    """
    try:
        res = post(url, headers={"Referer": url}, allow_redirects=False)
        return res.headers["location"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def devuploads(url):
    """
    Generate a direct download link for devuploads.com URLs.
    @param url: URL from devuploads.com
    @return: Direct download link
    """
    with Session() as session:
        res = session.get(url)
        html = HTML(res.text)
        if not html.xpath("//input[@name]"):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        data = {i.get("name"): i.get("value") for i in html.xpath("//input[@name]")}
        res = session.post("https://gujjukhabar.in/", data=data)
        html = HTML(res.text)
        if not html.xpath("//input[@name]"):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        data = {i.get("name"): i.get("value") for i in html.xpath("//input[@name]")}
        resp = session.get(
            "https://du2.devuploads.com/dlhash.php",
            headers={
                "Origin": "https://gujjukhabar.in",
                "Referer": "https://gujjukhabar.in/",
            },
        )
        if not resp.text:
            raise DirectDownloadLinkException("ERROR: Unable to find ipp value")
        data["ipp"] = resp.text.strip()
        if not data.get("rand"):
            raise DirectDownloadLinkException("ERROR: Unable to find rand value")
        randpost = session.post(
            "https://devuploads.com/token/token.php",
            data={"rand": data["rand"], "msg": ""},
            headers={
                "Origin": "https://gujjukhabar.in",
                "Referer": "https://gujjukhabar.in/",
            },
        )
        if not randpost:
            raise DirectDownloadLinkException("ERROR: Unable to find xd value")
        data["xd"] = randpost.text.strip()
        res = session.post(url, data=data)
        html = HTML(res.text)
        if not html.xpath("//input[@name='orilink']/@value"):
            raise DirectDownloadLinkException("ERROR: Unable to find Direct Link")
        direct_link = html.xpath("//input[@name='orilink']/@value")
        return direct_link[0]


def uploadhaven(url):
    """
    Generate a direct download link for uploadhaven.com URLs.
    @param url: URL from uploadhaven.com
    @return: Direct download link
    """
    try:
        res = get(url, headers={"Referer": "http://steamunlocked.net/"})
        html = HTML(res.text)
        if not html.xpath('//form[@method="POST"]//input'):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        data = {
            i.get("name"): i.get("value")
            for i in html.xpath('//form[@method="POST"]//input')
        }
        sleep(15)
        res = post(url, data=data, headers={"Referer": url}, cookies=res.cookies)
        html = HTML(res.text)
        if not html.xpath('//div[@class="alert alert-success mb-0"]//a'):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        a = html.xpath('//div[@class="alert alert-success mb-0"]//a')[0]
        return a.get("href")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def mediafile(url):
    """
    Generate a direct download link for mediafile.cc URLs.
    @param url: URL from mediafile.cc
    @return: Direct download link
    """
    try:
        res = get(url, allow_redirects=True)
        match = search(r"href='([^']+)'", res.text)
        if not match:
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        download_url = match[1]
        sleep(60)
        res = get(download_url, headers={"Referer": url}, cookies=res.cookies)
        postvalue = search(r"showFileInformation(.*);", res.text)
        if not postvalue:
            raise DirectDownloadLinkException("ERROR: Unable to find post value")
        postid = postvalue[1].replace("(", "").replace(")", "")
        response = post(
            "https://mediafile.cc/account/ajax/file_details",
            data={"u": postid},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        html = response.json()["html"]
        return [
            i for i in findall(r'https://[^\s"\']+', html) if "download_token" in i
        ][1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def mediafire(url, session=None):
    if "/folder/" in url:
        return mediafireFolder(url)
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ""
    if final_link := findall(
        r"https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+", url
    ):
        return final_link[0]

    def _decode_url(html, session):
        enc_url = html.xpath('//a[@id="downloadButton"]')
        if enc_url:
            final_link = enc_url[0].attrib.get('href')
            scrambled = enc_url[0].attrib.get('data-scrambled-url')

            if final_link and scrambled:
                try:
                    final_link = b64decode(scrambled).decode("utf-8")
                    return final_link
                except Exception as e:
                    raise ValueError(f"Failed to decode final link. {e.__class__.__name__}") from e
            elif final_link.startswith("http"):
                return final_link
            elif final_link.startswith("//"):
                return mediafire(f"https:{final_link}", session=session)
            else:
                raise ValueError("No download link found")
        else:
            raise ValueError("Download button not found in the HTML content. It may have been blocked by Cloudflare's anti-bot protection.")

    if session is None:
        session = create_scraper()
        parsed_url = urlparse(url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    try:
        html = HTML(session.get(url).text)
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if error := html.xpath('//p[@class="notranslate"]/text()'):
        session.close()
        raise DirectDownloadLinkException(f"ERROR: {error[0]}")
    if html.xpath("//div[@class='passwordPrompt']"):
        if not _password:
            session.close()
            raise DirectDownloadLinkException(
                f"ERROR: {PASSWORD_ERROR_MESSAGE}".format(url)
            )
        try:
            html = HTML(session.post(url, data={"downloadp": _password}).text)
        except Exception as e:
            session.close()
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if html.xpath("//div[@class='passwordPrompt']"):
            session.close()
            raise DirectDownloadLinkException("ERROR: Wrong password.")
    try:
        final_link = _decode_url(html, session)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}")
    session.close()
    return final_link


def osdn(url):
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if not (direct_link := html.xapth('//a[@class="mirror_link"]/@href')):
            raise DirectDownloadLinkException("ERROR: Direct link not found")
        return f"https://osdn.net{direct_link[0]}"


def yandex_disk(url: str) -> str:
    """Yandex.Disk direct link generator
    Based on https://github.com/wldhx/yadisk-direct"""
    try:
        link = findall(r"\b(https?://(yadi\.sk|disk\.yandex\.(com|ru))\S+)", url)[0][0]
    except IndexError:
        return "No Yandex.Disk links found\n"
    api = "https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}"
    try:
        return get(api.format(link)).json()["href"]
    except KeyError as e:
        raise DirectDownloadLinkException(
            "ERROR: File not found/Download limit reached"
        ) from e


def github(url):
    """GitHub direct links generator"""
    try:
        findall(r"\bhttps?://.*github\.com.*releases\S+", url)[0]
    except IndexError as e:
        raise DirectDownloadLinkException("No GitHub Releases links found") from e
    with create_scraper() as session:
        _res = session.get(url, stream=True, allow_redirects=False)
        if "location" in _res.headers:
            return _res.headers["location"]
        raise DirectDownloadLinkException("ERROR: Can't extract the link")


def hxfile(url):
    if not ospath.isfile("hxfile.txt"):
        raise DirectDownloadLinkException("ERROR: hxfile.txt (cookies) Not Found!")
    try:
        jar = MozillaCookieJar()
        jar.load("hxfile.txt")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    cookies = {cookie.name: cookie.value for cookie in jar}
    try:
        if url.strip().endswith(".html"):
            url = url[:-5]
        file_code = url.split("/")[-1]
        html = HTML(
            post(
                url,
                data={"op": "download2", "id": file_code},
                cookies=cookies,
            ).text
        )
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if direct_link := html.xpath("//a[@class='btn btn-dow']/@href"):
        header = [f"Referer: {url}"]
        return direct_link[0], header
    raise DirectDownloadLinkException("ERROR: Direct download link not found")


def onedrive(link):
    """Onedrive direct link generator
    By https://github.com/junedkh"""
    with create_scraper() as session:
        try:
            link = session.get(link).url
            parsed_link = urlparse(link)
            link_data = parse_qs(parsed_link.query)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if not link_data:
            raise DirectDownloadLinkException("ERROR: Unable to find link_data")
        folder_id = link_data.get("resid")
        if not folder_id:
            raise DirectDownloadLinkException("ERROR: folder id not found")
        folder_id = folder_id[0]
        authkey = link_data.get("authkey")
        if not authkey:
            raise DirectDownloadLinkException("ERROR: authkey not found")
        authkey = authkey[0]
        boundary = uuid4()
        headers = {"content-type": f"multipart/form-data;boundary={boundary}"}
        data = f"--{boundary}\r\nContent-Disposition: form-data;name=data\r\nPrefer: Migration=EnableRedirect;FailOnMigratedFiles\r\nX-HTTP-Method-Override: GET\r\nContent-Type: application/json\r\n\r\n--{boundary}--"
        try:
            resp = session.get(
                f'https://api.onedrive.com/v1.0/drives/{folder_id.split("!", 1)[0]}/items/{folder_id}?$select=id,@content.downloadUrl&ump=1&authKey={authkey}',
                headers=headers,
                data=data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if "@content.downloadUrl" not in resp:
        raise DirectDownloadLinkException("ERROR: Direct link not found")
    return resp["@content.downloadUrl"]


def pixeldrain(url):
    try:
        url = url.rstrip("/")
        code = url.split("/")[-1].split("?", 1)[0]
        response = get("https://pd.cybar.xyz/", allow_redirects=True)
        return response.url + code
    except Exception as e:
        raise DirectDownloadLinkException("ERROR: Direct link not found")


def streamtape(url):
    splitted_url = url.split("/")
    _id = splitted_url[4] if len(splitted_url) >= 6 else splitted_url[-1]
    try:
        html = HTML(get(url).text)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    script = html.xpath(
        "//script[contains(text(),'ideoooolink')]/text()"
    ) or html.xpath("//script[contains(text(),'ideoolink')]/text()")
    if not script:
        raise DirectDownloadLinkException("ERROR: requeries script not found")
    if not (link := findall(r"(&expires\S+)'", script[0])):
        raise DirectDownloadLinkException("ERROR: Download link not found")
    return f"https://streamtape.com/get_video?id={_id}{link[-1]}"


def racaty(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            json_data = {"op": "download2", "id": url.split("/")[-1]}
            html = HTML(session.post(url, data=json_data).text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if direct_link := html.xpath("//a[@id='uniqueExpirylink']/@href"):
        return direct_link[0]
    else:
        raise DirectDownloadLinkException("ERROR: Direct link not found")


def fichier(link):
    """1Fichier direct link generator
    Based on https://github.com/Maujar
    """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = match(regex, link)
    if not gan:
        raise DirectDownloadLinkException("ERROR: The link you entered is wrong!")
    if "::" in link:
        pswd = link.split("::")[-1]
        url = link.split("::")[-2]
    else:
        pswd = None
        url = link
    cget = create_scraper().request
    try:
        if pswd is None:
            req = cget("post", url)
        else:
            pw = {"pass": pswd}
            req = cget("post", url, data=pw)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if req.status_code == 404:
        raise DirectDownloadLinkException(
            "ERROR: File not found/The link you entered is wrong!"
        )
    html = HTML(req.text)
    if dl_url := html.xpath('//a[@class="ok btn-general btn-orange"]/@href'):
        return dl_url[0]
    if not (ct_warn := html.xpath('//div[@class="ct_warn"]')):
        raise DirectDownloadLinkException(
            "ERROR: Error trying to generate Direct Link from 1fichier!"
        )
    if len(ct_warn) == 3:
        str_2 = ct_warn[-1].text
        if "you must wait" in str_2.lower():
            if numbers := [int(word) for word in str_2.split() if word.isdigit()]:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute."
                )
            else:
                raise DirectDownloadLinkException(
                    "ERROR: 1fichier is on a limit. Please wait a few minutes/hour."
                )
        elif "protect access" in str_2.lower():
            raise DirectDownloadLinkException(
                f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(link)}"
            )
        else:
            raise DirectDownloadLinkException(
                "ERROR: Failed to generate Direct Link from 1fichier!"
            )
    elif len(ct_warn) == 4:
        str_1 = ct_warn[-2].text
        str_3 = ct_warn[-1].text
        if "you must wait" in str_1.lower():
            if numbers := [int(word) for word in str_1.split() if word.isdigit()]:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute."
                )
            else:
                raise DirectDownloadLinkException(
                    "ERROR: 1fichier is on a limit. Please wait a few minutes/hour."
                )
        elif "bad password" in str_3.lower():
            raise DirectDownloadLinkException(
                "ERROR: The password you entered is wrong!"
            )
    raise DirectDownloadLinkException(
        "ERROR: Error trying to generate Direct Link from 1fichier!"
    )


def solidfiles(url):
    """Solidfiles direct link generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18"""
    with create_scraper() as session:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
            }
            pageSource = session.get(url, headers=headers).text
            mainOptions = str(
                search(r"viewerOptions\'\,\ (.*?)\)\;", pageSource).group(1)
            )
            return loads(mainOptions)["downloadUrl"]
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e


def krakenfiles(url):
    with Session() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        html = HTML(_res.text)
        if post_url := html.xpath('//form[@id="dl-form"]/@action'):
            post_url = f"https://krakenfiles.com{post_url[0]}"
        else:
            raise DirectDownloadLinkException("ERROR: Unable to find post link.")
        if token := html.xpath('//input[@id="dl-token"]/@value'):
            data = {"token": token[0]}
        else:
            raise DirectDownloadLinkException("ERROR: Unable to find token for post.")
        try:
            _json = session.post(post_url, data=data).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__} While send post request"
            ) from e
    if _json["status"] not in ["ok", "success"]:
        raise DirectDownloadLinkException(
            "ERROR: Unable to download from krakenfiles. Check your link or try again later."
        )
    return _json["url"]


def uploadee(url):
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if link := html.xpath("//a[@id='d_l']/@href"):
            return link[0]
        else:
            raise DirectDownloadLinkException(
                "ERROR: Direct Download link not found. Check your link or try again later."
            )


def terabox(url):
    if not ospath.isfile("terabox.txt"):
        raise DirectDownloadLinkException("ERROR: terabox.txt not found")
    try:
        session = create_scraper()
        jar = MozillaCookieJar("terabox.txt")
        jar.load()
        session.cookies.update(jar)
        res = session.get(url)
        key = res.url.split("?surl=")[-1]
        res = session.get(
            f"https://www.terabox.com/share/list?app_id=250528&shorturl={key}&root=1"
        )
        result = res.json()["list"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if len(result) > 1:
        raise DirectDownloadLinkException(
            "ERROR: Can't download mutiple files. Check your link or try again later."
        )
    result = result[0]
    if result["isdir"] != "0":
        raise DirectDownloadLinkException("ERROR: Can't download folder.")
    return result["dlink"]


def filepress(url):
    cget = create_scraper().request
    try:
        url = cget("GET", url).url
        raw = urlparse(url)
        json_data = {
            "id": raw.path.split("/")[-1],
            "method": "publicDownlaod",
        }
        api = f"{raw.scheme}://{raw.hostname}/api/file/downlaod/"
        res = cget("POST", api, headers={"Referer": f"{raw.scheme}://{raw.hostname}"}, json=json_data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if "data" not in res:
        raise DirectDownloadLinkException(f"ERROR: {res['statusText']}")
    return f"https://drive.google.com/uc?id={res['data']}&export=download"


def gdtot(url):
    cget = create_scraper().request
    try:
        res = cget("GET", f"https://gdbot.xyz/file/{url.split('/')[-1]}")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    token_url = HTML(res.text).xpath(
        "//a[contains(@class,'inline-flex items-center justify-center')]/@href"
    )
    if not token_url:
        try:
            url = cget("GET", url).url
            p_url = urlparse(url)
            res = cget(
                "GET", f"{p_url.scheme}://{p_url.hostname}/ddl/{url.split('/')[-1]}"
            )
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if drive_link := findall(r"myDl\('(.*?)'\)", res.text):
            drive_link = drive_link[0]
            if drive_link.split("=")[-1] == "undefined":
                raise DirectDownloadLinkException(
                    "ERROR: File not found or user limit exceeded!"
                )
            else:
                return drive_link
        else:
            raise DirectDownloadLinkException(
                "ERROR: Drive Link not found. Check your link or try again later."
            )
    token_url = token_url[0]
    try:
        token_page = cget("GET", token_url)
    except Exception as e:
        raise DirectDownloadLinkException(
            f"ERROR: {e.__class__.__name__} with {token_url}"
        ) from e
    path = findall(r'"redirecturi"(.*)', token_page.text)
    if not path:
        raise DirectDownloadLinkException(
            "ERROR: Cannot bypass this. Check your link or try again later."
        )
    path = path[0].split('"')[1]
    raw = urlparse(token_url)
    final_url = f"{raw.scheme}://{raw.hostname}{path}"
    return sharer_scraper(final_url)


def sharer_scraper(url):
    cget = create_scraper().request
    try:
        url = cget("GET", url).url
        raw = urlparse(url)
        header = {
            "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10"
        }
        res = cget("GET", url, headers=header)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    key = findall(r"&key=([\w\d-]+)", url)
    if not key:
        raise DirectDownloadLinkException("ERROR: Key not found!")
    key = key[0]
    if not HTML(res.text).xpath("//button[@id='drc']"):
        raise DirectDownloadLinkException(
            "ERROR: This link don't have direct download button."
        )
    boundary = uuid4()
    headers = {
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
        "x-token": raw.hostname,
        "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10",
    }
    data = (
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n'
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n'
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n'
        f"------WebKitFormBoundary{boundary}--\r\n"
    )
    try:
        res = cget("POST", url, cookies=res.cookies, headers=headers, data=data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if "url" not in res:
        raise DirectDownloadLinkException(
            "ERROR: Drive Link not found. Check your link or try again later."
        )
    if "drive.google.com" in res["url"]:
        return res["url"]
    try:
        res = cget("GET", res["url"])
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if drive_link := HTML(res.text).xpath(
        "//a[contains(@class,'btn')]/@href"
    ) or HTML(res.text).xpath("//a[contains(@class,'btn btn-primary')]/@href"):
        return drive_link[0]
    else:
        raise DirectDownloadLinkException(
            "ERROR: Drive Link not found. Check your link or try again later."
        )


def wetransfer(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            splitted_url = url.split("/")
            json_data = {
                "security_hash": splitted_url[-1],
                "intent": "entire_transfer",
            }
            res = session.post(
                f"https://wetransfer.com/api/v4/transfers/{splitted_url[-2]}/download",
                json=json_data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if "direct_link" in res:
        return res["direct_link"]
    elif "message" in res:
        raise DirectDownloadLinkException(f"ERROR: {res['message']}")
    elif "error" in res:
        raise DirectDownloadLinkException(f"ERROR: {res['error']}")
    else:
        raise DirectDownloadLinkException("ERROR: cannot generate direct link")


def akmfiles(url):
    with create_scraper() as session:
        try:
            html = HTML(session.post(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if link := html.xpath("//a[@class='btn btn-success btn-lg']/@href"):
        return link[0]
    else:
        raise DirectDownloadLinkException(
            "ERROR: Direct Download link not found. Check your link or try again later."
        )


def shrdsk(url):
    with create_scraper() as session:
        try:
            _json = session.get(f"https://us-central1-affiliate2apk.cloudfunctions.net/get_data?shortid={url.split('/')[-1]}").json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if "download_data" not in _json:
        raise DirectDownloadLinkException("ERROR: Download data not found")
    try:
        _res = session.get(
            f"https://shrdsk.me/download/{_json['download_data']}", allow_redirects=False
        )
        return _res.headers["location"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e


def send_cm(url):
    if "/d/" in url:
        url = url.replace("/d/", "/files/")
    elif "/download/" in url:
        url = url.replace("/download/", "/files/")
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if link := HTML(_res.text).xpath(
            "//button[@data-download-url]/@data-download-url"
        ):
            return link[0]
        else:
            raise DirectDownloadLinkException(
                "ERROR: Direct Download link not found. Check your link or try again later."
            )


def tmpsend(url):
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
        if link := HTML(_res.text).xpath("//a[contains(@class,'btn-primary')]/@href"):
            return link[0]
        else:
            raise DirectDownloadLinkException(
                "ERROR: Direct Download link not found. Check your link or try again later."
            )


def gofile(url):
    try:
        if "::" in url:
            _password = url.split("::")[-1]
            _password = sha256(_password.encode("utf-8")).hexdigest()
            url = url.split("::")[-2]
        else:
            _password = ""
        _id = url.split("/")[-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if not _id:
        raise DirectDownloadLinkException("ERROR: Cannot find file id")
    try:
        _json = get(f"https://api.gofile.io/accounts/{_id}").json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _json["status"] != "ok":
        raise DirectDownloadLinkException(f"ERROR: {_json['data']}")
    _json2 = _json["data"]
    if _password:
        if _json2["password"] != _password:
            raise DirectDownloadLinkException("ERROR: Wrong password")
    if not _json2["downloadPage"]:
        raise DirectDownloadLinkException("ERROR: Download page not found")
    _res = get(_json2["downloadPage"]).text
    if not (link := findall(r'href="([^"]+)">Direct', _res)):
        raise DirectDownloadLinkException("ERROR: Direct link not found")
    return link[0]


def easyupload(url):
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ""
    file_id = url.split("/")[-1]
    if not file_id:
        raise DirectDownloadLinkException("ERROR: Cannot find file id")
    try:
        _res = get(url).text
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _password:
        if not findall(r'showFileInformation\(\)', _res):
            raise DirectDownloadLinkException("ERROR: Wrong password")
        _res = post(
            url,
            data={"key": file_id, "password": _password},
        ).text
    if not (link := findall(r'href="([^"]+)"\s*class="btn btn-primary mb-4"', _res)):
        raise DirectDownloadLinkException("ERROR: Direct link not found")
    return link[0]


def streamvid(url):
    file_code = url.split("/")[-1]
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.hostname}/d/{file_code}"
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if not (match := search(r'return\s+(\S+)\s\+\s(\S+)\.join\(""\)', _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    _js = match.group(1).replace('"', "") + match.group(2).replace('"', "")
    if not (match := search(rf"{_js}=\"([^\"]+)\"", _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    _token = match.group(1)
    _data = {"token": _token}
    try:
        _json = session.post(f"https://{parsed_url.hostname}/api/source/{file_code}", data=_data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _json["success"]:
        return _json["data"][0]["file"]
    else:
        raise DirectDownloadLinkException(f"ERROR: {_json['data']}")


def pcloud(url):
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if link := HTML(_res.text).xpath("//a[@id='downloadBtn']/@href"):
        return link[0]
    else:
        raise DirectDownloadLinkException(
            "ERROR: Direct Download link not found. Check your link or try again later."
        )


def qiwi(url):
    if "/folder/" in url:
        return qiwiFolder(url)
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ""
    file_id = url.split("/")[-1]
    if not file_id:
        raise DirectDownloadLinkException("ERROR: Cannot find file id")
    try:
        _res = get(url).text
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _password:
        if not findall(r'showFileInformation\(\)', _res):
            raise DirectDownloadLinkException("ERROR: Wrong password")
        _res = post(
            url,
            data={"key": file_id, "password": _password},
        ).text
    if not (link := findall(r'href="([^"]+)"\s*class="btn btn-primary mb-4"', _res)):
        raise DirectDownloadLinkException("ERROR: Direct link not found")
    return link[0]


def mp4upload(url):
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if not (match := search(r"wait\s*=\s*(\d+)", _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    sleep(int(match.group(1)))
    if not (match := search(r"file\s*:\s*'([^']+)'", _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    return match.group(1)


def berkasdrive(url):
    if "/folder/" in url:
        return berkasdriveFolder(url)
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ""
    file_id = url.split("/")[-1]
    if not file_id:
        raise DirectDownloadLinkException("ERROR: Cannot find file id")
    try:
        _res = get(url).text
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _password:
        if not findall(r'showFileInformation\(\)', _res):
            raise DirectDownloadLinkException("ERROR: Wrong password")
        _res = post(
            url,
            data={"key": file_id, "password": _password},
        ).text
    if not (link := findall(r'href="([^"]+)"\s*class="btn btn-primary mb-4"', _res)):
        raise DirectDownloadLinkException("ERROR: Direct link not found")
    return link[0]


def swisstransfer(url):
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if not (match := search(r'data-downloadurl="([^"]+)"', _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    return match.group(1)


def filelions_and_streamwish(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    file_code = url.split("/")[-1]
    if host == "filelions.co":
        api_url = f"https://{host}/api/file/direct_link"
    elif host in ["streamwish.to", "embedwish.com"]:
        api_url = f"https://{host}/e/l"
    else:
        api_url = f"https://{host}/api/download"
    client = Session()
    client.headers.update({"User-Agent": user_agent, "Referer": url})
    if host == "filelions.co":
        data = {"file_code": file_code}
    else:
        data = {"token": file_code}
    try:
        _res = client.post(api_url, data=data, allow_redirects=False).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _res["status"] == "success":
        return _res["result"]["url"]
    else:
        raise DirectDownloadLinkException(f"ERROR: {_res['msg']}")


def streamhub(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    file_code = url.split("/")[-1]
    api_url = f"https://{host}/api/download"
    client = Session()
    client.headers.update({"User-Agent": user_agent, "Referer": url})
    data = {"code": file_code}
    try:
        _res = client.post(api_url, data=data, allow_redirects=False).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _res["status"] == "success":
        return _res["data"]["downloadLink"]
    else:
        raise DirectDownloadLinkException(f"ERROR: {_res['message']}")


def linkBox(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    file_code = url.split("/")[-1]
    api_url = f"https://{host}/ajax.php"
    client = Session()
    client.headers.update({"User-Agent": user_agent, "Referer": url})
    data = {"ajax": "direct_link", "token": file_code}
    try:
        _res = client.post(api_url, data=data, allow_redirects=False).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _res["success"]:
        return _res["url"]
    else:
        raise DirectDownloadLinkException(f"ERROR: {_res['msg']}")


def doods(url):
    with create_scraper() as session:
        try:
            file_code = url.split("/")[-1]
            if not file_code:
                raise DirectDownloadLinkException("ERROR: Unable to find file code")
            parsed_url = urlparse(url)
            url = f"{parsed_url.scheme}://{parsed_url.hostname}/e/{file_code}"
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if not (match := search(r'return\s+(\S+)\s\+\s(\S+)\.join\(""\)', _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    _js = match.group(1).replace('"', "") + match.group(2).replace('"', "")
    if not (match := search(rf"{_js}=\"([^\"]+)\"", _res.text)):
        raise DirectDownloadLinkException("ERROR: Page source code changed")
    _token = match.group(1)
    _data = {"token": _token, "file_code": file_code}
    try:
        _json = session.post(f"https://{parsed_url.hostname}/api/source/{file_code}", data=_data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _json["success"]:
        return _json["data"][0]["file"]
    else:
        raise DirectDownloadLinkException(f"ERROR: {_json['data']}")


def mediafireFolder(url):
    try:
        raw = urlparse(url)
        folder_code = raw.path.split("/")[-1]
        api = f"https://www.mediafire.com/api/1.4/folder/get_info.php?r=utga&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key={folder_code}&response_format=json"
        res = get(api).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if res["response"]["result"] == "Error":
        raise DirectDownloadLinkException(f"ERROR: {res['response']['message']}")
    contents = res["response"]["folder_content"]["files"]
    details = {"contents": [], "title": "", "total_size": 0}
    for file in contents:
        if not file["filename"]:
            continue
        item = {
            "path": "",
            "filename": file["filename"],
            "url": file["links"]["normal_download"],
        }
        details["contents"].append(item)
        details["total_size"] += int(file["size"])
    details["title"] = res["response"]["folder_info"]["name"]
    return details


def qiwiFolder(url):
    try:
        folder_id = url.split("/")[-1]
        api = f"https://s2.qiwi.gg/api/folder/{folder_id}"
        res = get(api).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if res["status"] != "success":
        raise DirectDownloadLinkException(f"ERROR: {res['message']}")
    contents = res["data"]["files"]
    details = {"contents": [], "title": "", "total_size": 0}
    for file in contents:
        if not file["name"]:
            continue
        item = {
            "path": "",
            "filename": file["name"],
            "url": file["url"],
        }
        details["contents"].append(item)
        details["total_size"] += int(file["size"])
    details["title"] = res["data"]["name"]
    return details


def berkasdriveFolder(url):
    try:
        folder_id = url.split("/")[-1]
        api = f"https://berkasdrive.com/api/folder/{folder_id}"
        res = get(api).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if res["status"] != "success":
        raise DirectDownloadLinkException(f"ERROR: {res['message']}")
    contents = res["data"]["files"]
    details = {"contents": [], "title": "", "total_size": 0}
    for file in contents:
        if not file["name"]:
            continue
        item = {
            "path": "",
            "filename": file["name"],
            "url": file["url"],
        }
        details["contents"].append(item)
        details["total_size"] += int(file["size"])
    details["title"] = res["data"]["name"]
    return details
