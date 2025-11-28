from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import demjson3
import time


# ------------------------------------------------------
# Extract matchCentreData using JS object parsing
# ------------------------------------------------------
def get_match_data(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
    finally:
        driver.quit()

    # Find require.config.params["args"] = {...};
    pattern = r'require\.config\.params\["args"\]\s*=\s*(\{.*?\});'
    match = re.search(pattern, html, flags=re.DOTALL)

    if not match:
        raise Exception("Could not extract args JS object")

    js_text = match.group(1)

    # demjson3 handles JS-style objects better than json
    data = demjson3.decode(js_text)

    if "matchCentreData" not in data:
        raise Exception("matchCentreData not found in args")

    return data["matchCentreData"]


# ------------------------------------------------------
# Recursive preview for nested structures
# ------------------------------------------------------
def preview_nested(data, depth=0, max_depth=2):
    indent = "  " * depth
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{indent}{key:25} : dict ({len(value)} keys)")
                if depth < max_depth:
                    preview_nested(value, depth+1, max_depth)
            elif isinstance(value, list):
                print(f"{indent}{key:25} : list ({len(value)} items)")
                if depth < max_depth and len(value) > 0 and isinstance(value[0], (dict, list)):
                    preview_nested(value[0], depth+1, max_depth)
            elif isinstance(value, str):
                short = value if len(value) < 80 else value[:80] + "..."
                print(f"{indent}{key:25} : str \"{short}\"")
            elif value is None:
                print(f"{indent}{key:25} : None")
            else:
                print(f"{indent}{key:25} : {type(value).__name__} {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{indent}[{i}] : {type(item).__name__}")
            if depth < max_depth:
                preview_nested(item, depth+1, max_depth)
    else:
        print(f"{indent}{data}")


# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
url = "https://www.whoscored.com/matches/1554706/live/england-league-two-2021-2022-sutton-united-salford-city"

match = get_match_data(url)
print("\n=== matchCentreData structure preview ===")
preview_nested(match, max_depth=3)  # change max_depth to explore deeper

 
