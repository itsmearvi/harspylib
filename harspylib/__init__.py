"""
harspylib
---------
A collection of Python utilities:
- Amortization calculator
- HTML link scraper (local)
- XPath link scraper (web, static + dynamic)
"""

__version__ = "0.1.0"

# Optionally expose submodules directly
from . import amort
from . import htmlscraper
from . import xlinkscraper
