import asyncio
from typing import Set, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
import os
import random
import aiohttp
from bs4 import BeautifulSoup

# Lista de User-Agents para evitar bloqueos por firmas estáticas
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

BAD_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".rar", ".mp4", ".mp3", ".docx", ".xlsx"}
BAD_SCHEMES = {"mailto:", "javascript:", "tel:", "data:"}
BAD_DOMAINS = {"facebook.com", "twitter.com", "instagram.com", "tiktok.com", "linkedin.com", "youtube.com", "x.com"}

STATUS_MESSAGES = {
    200: "OK",
    301: "Moved Permanently",
    302: "Found",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    429: "Too Many Requests",
    500: "Internal Server Error",
}

def is_valid_url(url: str) -> bool:
    url_lower = url.lower()
    
    if any(url_lower.startswith(scheme) for scheme in BAD_SCHEMES):
        return False

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    
    # Protección perimetral básica contra SSRF
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0") or hostname.startswith("192.168.") or hostname.startswith("10."):
        return False

    _, ext = os.path.splitext(parsed.path)
    if ext.lower() in BAD_EXTENSIONS:
        return False

    if any(domain in hostname for domain in BAD_DOMAINS):
        return False

    return True

async def fetch_and_parse(session: aiohttp.ClientSession, url: str) -> Tuple[str, int, str, List[str]]:
    """
    Realiza la petición HTTP, maneja el estado y extrae enlaces si corresponde.
    """
    try:
        # allow_redirects=False es clave: queremos validar el enlace tal y como está, 
        # si redirige, reportamos el 301/302.
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=False) as response:
            status = response.status
            msg = STATUS_MESSAGES.get(status, "Unknown")
            
            content_type = response.headers.get("Content-Type", "")
            if status != 200 or "text/html" not in content_type:
                return url, status, msg, []

            html = await response.text(errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            found_links = []
            
            for tag in soup.find_all("a", href=True):
                href = tag["href"].strip()
                if not href or not is_valid_url(href):
                    continue
                
                absolute = urljoin(url, href).split("#")[0]
                found_links.append(absolute)
                
            return url, status, msg, found_links

    except asyncio.TimeoutError:
        return url, 408, "Request Timeout", []
    except aiohttp.ClientSSLError:
        return url, 0, "SSL/TLS Certificate Error", []
    except aiohttp.ClientError:
        return url, 0, "Network Request Error", []
    except Exception as e:
        return url, 0, f"Error: {type(e).__name__}", []

async def process_url_batch(links: List[str]) -> List[Tuple[str, int, str, List[str]]]:
    """
    Gestiona la ejecución por lotes controlando la concurrencia mediante un Semáforo.
    """
    sem = asyncio.Semaphore(10)  # Máximo 10 peticiones simultáneas totales
    
    # ssl=False permite que el script siga analizando aunque la web tenga el certificado roto
    connector = aiohttp.TCPConnector(limit_per_host=3, ssl=False)
    
    # Rotamos el User-Agent para la sesión de este lote
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async def sem_task(link):
            async with sem:
                await asyncio.sleep(0.05)  # Cortesía anti-bloqueo
                return await fetch_and_parse(session, link)
        
        tasks = [sem_task(link) for link in links]
        return await asyncio.gather(*tasks)