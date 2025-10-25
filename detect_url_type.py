import requests
from bs4 import BeautifulSoup
import pandas as pd

def analyze_url(url):
    result = {"url": url, "status": "", "type": "", "has_table": False, "is_js_rendered": False, "is_json_api": False}
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text
        result["status"] = resp.status_code

        # 静态 HTML 检查
        if "<table" in html:
            result["has_table"] = True

        # JSON-LD / API特征
        if "application/ld+json" in html or ".json" in html:
            result["is_json_api"] = True

        # JS渲染特征：React/Vue等占主导 + 空div结构
        if html.count("<script") > 10 and len(html) < 8000:
            result["is_js_rendered"] = True
        if "react" in html.lower() or "vue" in html.lower() or "axios" in html.lower():
            result["is_js_rendered"] = True

        # 类型分类
        if result["is_json_api"]:
            result["type"] = "json_api"
        elif result["is_js_rendered"]:
            result["type"] = "dynamic"
        elif result["has_table"]:
            result["type"] = "static_table"
        else:
            result["type"] = "static_text"

    except Exception as e:
        result["status"] = "error"
        result["type"] = "unknown"

    return result


df1 = pd.read_csv('immi_homefair_sitemap.txt',header=None, names=['urls'])
df2 = pd.read_csv('"wa_sitemap.txt',header=None, names=['urls'])