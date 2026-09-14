#!/usr/bin/env python3
"""Discover all posts of a blog: sitemap -> RSS/Atom feed -> homepage links.

Usage: discover.py <blog-base-url>

Prints one line per discovered post:  <url>\t<title-or-empty>
Only stdlib, no dependencies.
"""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

UA = {"User-Agent": "Mozilla/5.0 (compatible; blog-paparazzi/1.0)"}

FEED_PATHS = ["/feed", "/rss", "/rss.xml", "/atom.xml", "/index.xml",
              "/feed.xml", "/feed/", "/rss/"]
SITEMAP_PATHS = ["/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml",
                 "/post-sitemap.xml", "/sitemap.txt"]

NON_POST_PAT = re.compile(
    r"(tag|categor|author|page/\d|archive|search|about|contact|privacy|"
    r"license|friends|links|guestbook|comment|feed|rss|atom|sitemap|"
    r"\.css|\.js|\.png|\.jpg|\.jpeg|\.gif|\.svg|\.ico|\.woff)",
    re.I)


def fetch(url, timeout=20):
    """Return (text, final_url) or (None, url) on failure. Follows redirects,
    so final_url may differ from url when the site has moved domains."""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace"), r.geturl()
    except Exception:
        return None, url


def strip_ns(tag):
    return tag.rsplit("}", 1)[-1].lower()


def parse_feed(text):
    """Return list of (url, title) from RSS/Atom XML."""
    out = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return out
    for el in root.iter():
        name = strip_ns(el.tag)
        if name == "item":  # RSS
            url = title = ""
            for c in el:
                cn = strip_ns(c.tag)
                if cn == "link" and c.text:
                    url = c.text.strip()
                elif cn == "title" and c.text:
                    title = c.text.strip()
            if url:
                out.append((url, title))
        elif name == "entry":  # Atom
            url = title = ""
            for c in el:
                cn = strip_ns(c.tag)
                if cn == "link" and c.get("href") and \
                        c.get("rel", "alternate") == "alternate":
                    url = c.get("href")
                elif cn == "title" and c.text:
                    title = c.text.strip()
            if url:
                out.append((url, title))
    return out


def parse_sitemap(text):
    """Return (sitemap_index_children, urls) from sitemap XML."""
    children, urls = [], []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return children, urls
    kind = strip_ns(root.tag)
    for el in root:
        for c in el:
            if strip_ns(c.tag) == "loc" and c.text:
                loc = c.text.strip()
                if kind == "sitemapindex":
                    children.append(loc)
                else:
                    urls.append(loc)
    return children, urls


def looks_like_post(url, base_host):
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    if p.netloc and p.netloc != base_host:
        return False
    path = p.path.rstrip("/")
    if not path or path == "/":
        return False
    if re.fullmatch(r"/(link|links|about|archives|tags|categories|msg|board)",
                    path, re.I):
        return False
    if NON_POST_PAT.search(path):
        return False
    return True


def scan_listing(html_text, base, host, found):
    """Extract post (url, title) pairs from a listing page's anchors.

    Anchors may nest tags (<span>, <img>) between <a> and text, so strip
    inner markup; keep the longest non-empty title per url.
    """
    for m in re.finditer(
            r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', html_text, re.S):
        url = urljoin(base, m.group(1))
        inner = re.sub(r"<[^>]+>", "", m.group(2))
        title = re.sub(r"\s+", " ", inner).strip()[:200]
        if looks_like_post(url, host):
            cur = found.get(url)
            if cur is None or (title and len(title) > len(cur)):
                found[url] = title


def main():
    base = sys.argv[1].rstrip("/")
    found = {}  # url -> title

    # Probe homepage once to detect a domain migration (e.g. old blog
    # redirects wholesale to a new host); if so, rebase everything.
    home, final = fetch(base + "/")
    host = urlparse(final).netloc or urlparse(base).netloc
    base = f"{urlparse(final).scheme}://{host}" if host else base

    # 1. sitemaps
    for sp in SITEMAP_PATHS:
        text, _ = fetch(base + sp)
        if not text:
            continue
        children, urls = parse_sitemap(text)
        if children:
            for child in children[:20]:
                ct, _ = fetch(child)
                if ct:
                    _, cu = parse_sitemap(ct)
                    urls.extend(cu)
        for u in urls:
            if looks_like_post(u, host):
                found.setdefault(u, "")
        if found:
            break

    # 2. feeds (add titles where sitemap had none)
    for fp in FEED_PATHS:
        text, _ = fetch(base + fp)
        if not text:
            continue
        entries = parse_feed(text)
        for url, title in entries:
            if looks_like_post(url, host):
                if url in found and title:
                    found[url] = title
                else:
                    found.setdefault(url, title)
        if entries:
            break

    # 3. listing crawl: homepage + pagination (/page/N/, ?paged=N) until
    #    a page 404s or adds no new posts; also try /archives/.
    #    Feeds are often capped at 10-20 items, sitemaps may 404 — the
    #    paginated listing is the ground truth on Hexo/Hugo/WordPress.
    def listing_pages():
        yield base + "/", home
        for n in range(2, 51):
            yield f"{base}/page/{n}/", None

    stall = 0
    for page, prefetched in listing_pages():
        html = prefetched if prefetched is not None else fetch(page)[0]
        if html is None:
            stall += 1
            if stall >= 2 or page != base + "/":
                break
            continue
        before = len(found)
        scan_listing(html, base + "/", host, found)
        if len(found) == before and page != base + "/":
            break
        stall = 0
    arch, _ = fetch(base + "/archives/")
    if arch:
        scan_listing(arch, base + "/", host, found)

    for url, title in sorted(found.items()):
        print(f"{url}\t{title}")
    print(f"# total: {len(found)}", file=sys.stderr)


if __name__ == "__main__":
    main()
