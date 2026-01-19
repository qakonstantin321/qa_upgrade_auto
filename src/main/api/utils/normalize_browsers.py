def norm_browser_name(val) -> str:
    s = str(val).strip().lower()
    return {"chrome": "chromium", "ff": "firefox"}.get(s, s)
