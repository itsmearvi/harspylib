# htmlscraper.py

**Simplified Local HTML Scraper** (we’ll call it **`htmlscraper.py`**)

   * Lightweight, static-only
   * Works on **local HTML files**
   * Uses `BeautifulSoup` (no Selenium required)
   * Generates `_full.md` and `_relative.md` from `<a>` tags

Extract links from a **local HTML file**.
Lightweight, static-only (no Selenium required).

## Features

* Works with saved/local HTML files.
* Optional `--baseurl` to resolve relative paths.
* Generates the same two Markdown reports:

  * `<filename>_full.md`
  * `<filename>_relative.md`

## Usage

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