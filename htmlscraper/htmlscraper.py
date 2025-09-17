#!/usr/bin/env python3
"""
htmlscraper.py
--------------
Extract anchor links from a local HTML file.
Generates two Markdown files:
  - <filename>_full.md     → [Anchor Text](Resolved URL)
  - <filename>_relative.md → Base URL + relative paths
"""

import argparse
import os
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def clean_text(raw_text: str) -> str:
    """Normalize whitespace in anchor text."""
    return re.sub(r"\s+", " ", (raw_text or "").strip())


def process_html(content, base_name, base_url=""):
    """Parse HTML and export two Markdown files."""
    soup = BeautifulSoup(content, "html.parser")

    # If HTML has <base>, override base_url
    base_tag = soup.find("base")
    if base_tag and base_tag.get("href"):
        base_url = base_tag["href"]

    output_md_full = base_name + "_full.md"
    output_md_relative = base_name + "_relative.md"

    full_markdown_lines = []
    relative_urls = []

    for a in soup.find_all("a", href=True):
        anchor_text = clean_text(a.get_text())
        href = a.get("href")
        if not href:
            continue

        # Resolved absolute URL
        resolved = urljoin(base_url, href) if base_url else href
        full_markdown_lines.append(f"- [{anchor_text}]({resolved})")

        # Only keep relative links
        if href.startswith("/"):
            relative_urls.append(href)
        else:
            parsed = urlparse(resolved)
            base_parsed = urlparse(base_url)
            if base_url and parsed.netloc == base_parsed.netloc:
                relative_urls.append(parsed.path)

    # Write full markdown
    with open(output_md_full, "w", encoding="utf-8") as f:
        f.write("\n".join(full_markdown_lines))

    # Write relative markdown
    with open(output_md_relative, "w", encoding="utf-8") as f:
        f.write(f"Base URL: {base_url}\n\n")
        f.write("\n".join(f"- {rel}" for rel in sorted(set(relative_urls))))

    print(f"✅ Exported {len(full_markdown_lines)} links")
    print(f"   → {output_md_full} (anchors + full URLs)")
    print(f"   → {output_md_relative} (base + relative URLs)")


def main():
    parser = argparse.ArgumentParser(
        description="html_link_scraper: Extract links from a local HTML file and export Markdown reports."
    )
    parser.add_argument(
        "--htmlfile", "-i", required=True,
        help="Path to the input HTML file"
    )
    parser.add_argument(
        "--baseurl", "-b", default="",
        help="Optional base URL for resolving relative links (default: none)"
    )

    args = parser.parse_args()

    base_name, _ = os.path.splitext(args.htmlfile)
    with open(args.htmlfile, "r", encoding="utf-8") as f:
        content = f.read()
    process_html(content, base_name, args.baseurl)


if __name__ == "__main__":
    main()
