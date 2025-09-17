#!/usr/bin/env python3
"""
xlinkscraper.py
---------------
A Python utility to extract anchor links from static or dynamic web pages using XPath.
Supports recursive traversal of clickable elements (e.g., buttons) with Selenium.
"""

import argparse
import time
import re
from urllib.parse import urljoin, urlparse

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_static_html(url):
    """Fetch static HTML using requests."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def fetch_dynamic_driver(url, headless=True):
    """Initialize Selenium and return driver with page loaded."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")  # force desktop layout
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Ensure page <body> is loaded
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    return driver


def normalize_xpath(xpath_expr):
    """Ensure XPath always searches for anchors recursively (static mode only)."""
    xp = xpath_expr.strip()
    if not xp.endswith("a") and not xp.endswith("a]"):
        xp = xp + "//a"
    elif xp.endswith("/a"):
        xp = xp[:-2] + "//a"
    return xp


def clean_text(raw_text):
    """Normalize whitespace in anchor text."""
    return re.sub(r"\s+", " ", (raw_text or "").strip())


def collect_links_and_targets(element, click_xpath=None):
    """Collect anchors and clickable elements under a Selenium element."""
    anchors = element.find_elements(By.TAG_NAME, "a")
    if click_xpath:
        targets = element.find_elements(By.XPATH, click_xpath)
    else:
        targets = element.find_elements(By.TAG_NAME, "button")
    return anchors, targets


def recursive_traverse(driver, element, base_url, collected_links, visited, maxdepth, click_xpath, scope_xpath):
    """Recursive DFS traversal of anchors and clickable expanders."""
    anchors, targets = collect_links_and_targets(element, click_xpath)

    # Collect anchors
    for a in anchors:
        href = a.get_attribute("href")
        text = clean_text(a.text)
        if not href:
            continue
        resolved = urljoin(base_url, href)
        collected_links.append((text, resolved, href))

    # Process clickable elements
    for tgt in targets:
        if tgt in visited:
            continue
        visited.add(tgt)

        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", tgt)
            tgt.click()
            time.sleep(1)  # allow DOM update
        except Exception as e:
            print(f"⚠️ Could not click element: {e}")
            continue

        # Re-scope to original container
        try:
            container = driver.find_element(By.XPATH, scope_xpath)
        except Exception:
            container = element

        if maxdepth is None or maxdepth > 0:
            recursive_traverse(
                driver,
                container,
                base_url,
                collected_links,
                visited,
                maxdepth=maxdepth,
                click_xpath=click_xpath,
                scope_xpath=scope_xpath,
            )


def extract_links_dynamic(url, top_xpath, maxdepth=None, click_xpath=None, headless=True):
    """Extract links recursively from a dynamic page starting at top_xpath."""
    driver = fetch_dynamic_driver(url, headless=headless)

    try:
        elements = driver.find_elements(By.XPATH, top_xpath)
        if not elements:
            print(f"⚠️ No elements found for XPath: {top_xpath}")
            return [], []

        collected_links = []
        visited = set()

        for element in elements:
            recursive_traverse(
                driver,
                element,
                url,
                collected_links,
                visited,
                maxdepth=maxdepth,
                click_xpath=click_xpath,
                scope_xpath=top_xpath,
            )

        relative_links = make_relative_links(collected_links, url)
        return collected_links, relative_links

    finally:
        driver.quit()


def make_relative_links(collected_links, base_url):
    """Convert absolute URLs into relative paths if they belong to the same domain."""
    relative_links = []
    base_parsed = urlparse(base_url)
    base_prefix = f"{base_parsed.scheme}://{base_parsed.netloc}"

    for _, resolved, _ in collected_links:
        if resolved.startswith(base_prefix):
            rel = resolved[len(base_prefix):] or "/"
            relative_links.append(rel)
    return sorted(set(relative_links))


def write_markdown_files(collected_links, relative_links, base_url, filename_prefix):
    """Write results to Markdown files."""
    full_md = filename_prefix + "_full.md"
    with open(full_md, "w", encoding="utf-8") as f:
        for text, resolved, _ in collected_links:
            f.write(f"- [{text}]({resolved})\n")

    rel_md = filename_prefix + "_relative.md"
    with open(rel_md, "w", encoding="utf-8") as f:
        f.write(f"Base URL: {base_url}\n\n")
        f.write("\n".join(f"- {rel}" for rel in relative_links))

    print(f"✅ Extracted {len(collected_links)} links")
    print(f"   → {full_md} (anchors + full URLs)")
    print(f"   → {rel_md} (base + relative URLs)")


def main():
    parser = argparse.ArgumentParser(
        description="xlinkscraper: Extract anchor links from static or dynamic web pages using XPath. "
                    "Supports recursive traversal of clickable elements at any depth."
    )
    parser.add_argument("--url", "-u", required=True, help="Web page URL to fetch")
    parser.add_argument("--xpath", "-x", required=True, help="Top-level XPath container")
    parser.add_argument("--filename", "-f", required=True, help="Prefix for output markdown files")
    parser.add_argument("--dynamic", "-d", action="store_true", help="Enable dynamic mode with Selenium")
    parser.add_argument("--maxdepth", "-m", type=int, default=None,
                        help="Maximum recursion depth per subtree (default: unlimited)")
    parser.add_argument("--clickxpath", "-c",
                        help="XPath to identify clickable elements (default: <button>)")
    parser.add_argument("--no-headless", action="store_true", help="Run Selenium with a visible browser window")

    args = parser.parse_args()

    if args.dynamic:
        collected_links, relative_links = extract_links_dynamic(
            args.url, args.xpath, args.maxdepth, args.clickxpath, headless=not args.no_headless
        )
    else:
        # Static scrape
        content = fetch_static_html(args.url)
        tree = html.fromstring(content)
        xpath_normalized = normalize_xpath(args.xpath)
        anchors = tree.xpath(xpath_normalized)

        collected_links = []
        for a in anchors:
            href = a.get("href")
            text = clean_text(a.text_content())
            if not href:
                continue
            resolved = urljoin(args.url, href)
            collected_links.append((text, resolved, href))

        relative_links = make_relative_links(collected_links, args.url)

    if collected_links:
        write_markdown_files(collected_links, relative_links, args.url, args.filename)
    else:
        print("⚠️ No links found.")


if __name__ == "__main__":
    main()


# some web page `ma`y have dynamic content loaded so in that case use click path and give where to click e.g. if click path has id "//button[@id='expand']" otherwise use corresponding attribute //"//button[@class='fern-sidebar-link']"
# /html/body/div[1]/main/aside/div[3]
# /html/body/div[1]/main/aside/div[3]

# https://api.qdrant.tech/api-reference /html/body/div[1]/main/aside/div[3]