# 📦 harspylib Release Build Guide

This document describes the step-by-step process to build, test, and release new versions of **harspylib**.

---

## 🔧 1. Update Version

Edit `pyproject.toml` and bump the version number:

```toml
[project]
name = "harspylib"
version = "0.1.1"   # <-- bump this
```

Follow [semantic versioning](https://semver.org/):
- Patch: bug fixes → `0.1.1`
- Minor: new features → `0.2.0`
- Major: breaking changes → `1.0.0`

---

## 🔧 2. Clean Old Builds

Remove previous build artifacts:

```bash
rm -rf build/ dist/ *.egg-info
```

---

## 🔧 3. Build Package

Run:

```bash
python -m build
```

This will create:

```
dist/
  harspylib-x.y.z.tar.gz
  harspylib-x.y.z-py3-none-any.whl
```

---

## 🔧 4. Test Locally

Install the wheel in a clean venv:

```bash
pip install dist/harspylib-x.y.z-py3-none-any.whl --force-reinstall
```

Verify:

```bash
xlinkscraper --help
htmlscraper --help
amort --help
```

Also test imports:

```python
from harspylib.htmlscraper import process_html
from harspylib.xlinkscraper import extract_links_dynamic
from harspylib.amort import amort_cli
```

---

## 🔧 5. Publish to TestPyPI

Upload to sandbox:

```bash
twine upload --repository testpypi dist/*
```

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple harspylib
```

Test as in step 4.

---

## 🔧 6. Publish to PyPI

Once satisfied:

```bash
twine upload dist/*
```

Install from PyPI:

```bash
pip install harspylib
```

---

## 🔧 7. Tag Release in Git

Tag the release version:

```bash
git tag v0.1.1
git push origin v0.1.1
```

---

## ✅ Summary

Each release workflow:

1. Bump version in `pyproject.toml`
2. Clean old builds
3. Build with `python -m build`
4. Test locally
5. Upload to **TestPyPI**
6. Upload to **PyPI**
7. Tag and push to GitHub

