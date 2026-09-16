#!/usr/bin/env python3
"""Verify every markdown link in a file returns HTTP 200.

Usage: check_links.py <markdown-file>
Prints broken links; exits 0 if all OK, 1 otherwise.
"""
import re
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; paparazzi/1.0)"}


def main():
    text = open(sys.argv[1], encoding="utf-8").read()
    urls = sorted(set(re.findall(r"\]\((https?://[^)\s]+)\)", text)))
    bad = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=UA, method="HEAD")
            code = urllib.request.urlopen(req, timeout=20).status
        except Exception:
            try:
                req = urllib.request.Request(url, headers=UA)
                code = urllib.request.urlopen(req, timeout=20).status
            except Exception as e:
                bad.append((url, str(e)[:80]))
                continue
        if code >= 400:
            bad.append((url, f"HTTP {code}"))
    for url, err in bad:
        print(f"BROKEN {url}  {err}")
    print(f"# checked {len(urls)} links, {len(bad)} broken", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
