# 📚 harspylib

**harspylib** is a Python utilities library containing multiple modules for automation, scraping, and data processing.  
Each module is self-contained but designed to work together under the same package.  

---

## ✨ Features

- Organized into modules for clarity and reuse.
- Provides both **CLI scripts** and **Python APIs**.
- Covers a growing set of tools:
  - **Amortization calculator**  
  - **HTML link scraper** (for local static HTML)  
  - **XPath link scraper** (for web pages, static + dynamic)  

---

## 📦 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/itsmearvi/harspylib.git
cd harspylib
pip install -r requirements.txt
```

Dependencies include:
- `requests`
- `lxml`
- `selenium`
- `beautifulsoup4`

---

## 🧰 Modules

### 1. `amort`
Amortization utilities for calculating and exporting loan repayment schedules.  

**Usage (CLI):**
```bash
python3 -m harspylib.amort.amort_tool --help
```

**Usage (API):**
```python
from harspylib.amort import amort_tool

schedule = amort_tool.generate_schedule(principal=1000, rate=0.05, months=12)
print(schedule)
```

---

### 2. `htmlscraper`
Scrapes anchor links from **local static HTML files**.  
Outputs two Markdown reports: `_full.md` and `_relative.md`.

**Usage (CLI):**
```bash
python3 -m harspylib.htmlscraper.htmlscraper \
  --htmlfile test.html \
  --baseurl https://example.com
```

**Usage (API):**
```python
from harspylib.htmlscraper import htmlscraper

with open("test.html", "r", encoding="utf-8") as f:
    content = f.read()
htmlscraper.process_html(content, base_name="test", base_url="https://example.com")
```

---

### 3. `xlinkscraper`
Scrapes anchor links from **web pages** using XPath.  
Supports dynamic pages (React/Next.js) with Selenium, recursive button expansion, and headless browsing.  

**Usage (CLI):**
```bash
python3 -m harspylib.xlinkscraper.xlinkscraper \
  --url https://api.qdrant.tech/api-reference \
  --xpath "/html/body/div[1]/main/aside/div[3]" \
  --filename qdrant-api-help \
  --dynamic \
  --clickxpath "//button[contains(@class,'fern-sidebar-link')]"
```

**Usage (API):**
```python
from harspylib.xlinkscraper import xlinkscraper

collected_links, relative_links = xlinkscraper.extract_links_dynamic(
    url="https://api.qdrant.tech/api-reference",
    top_xpath="/html/body/div[1]/main/aside/div[3]",
    maxdepth=2,
    click_xpath="//button[contains(@class,'fern-sidebar-link')]",
    headless=True
)
```

---

## ⚖️ License & Disclaimer

- Licensed under the **MIT License**.  
- Provided for **educational and personal use only**.  
- When scraping external websites, ensure you comply with their **Terms of Service** and **robots.txt**.  
- Use responsibly and at your own risk.

---

## 👤 Author

Maintained by **Arvind Hariharan**  
GitHub: [itsmearvi](https://github.com/itsmearvi)
