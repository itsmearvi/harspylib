# Link Scraping Utilities

This repo contains **two Python utilities** for extracting anchor links (`<a href="...">`) into Markdown reports.

1. **`xlinkscraper.py`**

   * Advanced tool
   * Works with URLs (static + dynamic)
   * Handles recursion, `--clickxpath`, `--maxdepth`, headless Selenium, etc.

2. **Simplified Local HTML Scraper** (we’ll call it **`htmlscraper.py`**)

   * Lightweight, static-only
   * Works on **local HTML files**
   * Uses `BeautifulSoup` (no Selenium required)
   * Generates `_full.md` and `_relative.md` from `<a>` tags
---

## Requirements

- Python 3.8+
- Dependencies:
  ```bash
    pip install requests lxml selenium
  ```

* Chrome browser + ChromeDriver installed.


## 1. xlinkscraper.py

Extract links from **web pages** (static or dynamic) using **XPath**.  
Supports recursive expansion of clickable elements (buttons, divs, etc.) via Selenium.

### Features
- Works with static and dynamic pages.
- Recursively expands clickable elements with `--clickxpath`.
- Supports `--maxdepth` recursion limits.
- Handles **absolute XPaths with array indices**.
- Runs in **headless** or visible browser mode.

## CLI Options

| Option             | Description                                                                    |
| ------------------ | ------------------------------------------------------------------------------ |
| `--url, -u`        | Web page URL (required)                                                        |
| `--xpath, -x`      | Top-level XPath container (absolute/relative, array indices supported)         |
| `--filename, -f`   | Prefix for output files (e.g., `links` → `links_full.md`, `links_relative.md`) |
| `--dynamic, -d`    | Enable Selenium for dynamic content (JS-driven sites)                          |
| `--clickxpath, -c` | XPath for clickable elements (default: `<button>`)                             |
| `--maxdepth, -m`   | Maximum recursion depth per subtree (default: unlimited)                       |

### Usage
```bash
# Dynamic page with sidebar expansion
python3 xlinkscraper.py \
  --url https://api.xyz.tech/api-reference \
  --xpath "/html/body/div[1]/main/aside/div[3]" \
  --filename online-api-help \
  --dynamic \
  --clickxpath "//button[contains(@class,'site-side-bar-links')]"
```

Output:

* `online-api-help_full.md` → all `[anchor text](absolute url)`
* `online-api-help_relative.md` → relative paths

---

## 2. htmlscraper.py

Extract links from a **local HTML file**.
Lightweight, static-only (no Selenium required).

### Features

* Works with saved/local HTML files.
* Optional `--baseurl` to resolve relative paths.
* Generates the same two Markdown reports:

  * `<filename>_full.md`
  * `<filename>_relative.md`

### Usage

```bash
# Extract from local file
python3 htmlscraper.py \
  --htmlfile test.html \
  --baseurl https://example.com
```

Output:

* `test_full.md` → all `[anchor text](absolute url)`
* `test_relative.md` → relative paths resolved with `--baseurl`

---

## Installation

1. Install Python 3.8+
2. Install dependencies:

   ```bash
   pip install requests lxml selenium beautifulsoup4
   ```
3. Ensure Chrome + ChromeDriver are installed for `xlinkscraper.py`.

---

## Notes

* Use **`xlinkscraper.py`** when dealing with **dynamic sites** (React/Next.js) or you need recursive button expansion.
* Use **`htmlscraper.py`** when working with **local HTML files** or simple static scraping.

---

## Disclaimer

This utility is provided for **educational and personal use only**.  
When using it on websites you do not own, please ensure you comply with the site's **Terms of Service** and **robots.txt** rules.  

The authors of this tool are **not responsible** for any misuse, including but not limited to:  
- Excessive scraping or denial of service.  
- Violation of website usage policies.  
- Legal or compliance issues arising from scraping protected content.  

Use responsibly and at your own risk.

---

## 📄 License

MIT — Free for personal and commercial use.

---

## Contact

For questions, feedback, or feature requests, reach out at **[itsmearvihar@gmail.com](mailto:itsmearvihar@gmail.com)**