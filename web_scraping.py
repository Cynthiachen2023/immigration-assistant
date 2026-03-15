import json
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36"
}

def clean_text(text: str) -> str:
    return " ".join(text.split())

def crawl_static_text(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=12)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = clean_text(soup.title.get_text()) if soup.title else ""
    paragraphs = [clean_text(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
    content = "\n\n".join([p for p in paragraphs if p])
    
    return {
        "url": url,
        "title": title,
        "content": content,
        "status": resp.status_code,
        "type": "static_text"
    }

def crawl_static_table(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=12)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = clean_text(soup.title.get_text()) if soup.title else ""
    
    tables = []
    for t in soup.find_all("table"):
        tables.append(clean_text(t.get_text(" ", strip=True)))
    
    paragraphs = [clean_text(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
    content = "\n\n".join([p for p in paragraphs if p])
    
    return {
        "url": url,
        "title": title,
        "content": content,
        "tables": tables,
        "status": resp.status_code,
        "type": "static_table"
    }

def crawl_json_api(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=12)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = clean_text(soup.title.get_text()) if soup.title else ""
    
    jsonld_items = []
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = (s.string or s.get_text() or "").strip()
        if raw:
            jsonld_items.append(json.loads(raw))
    
    return {
        "url": url,
        "title": title,
        "content": "",
        "jsonld": jsonld_items,
        "status": resp.status_code,
        "type": "json_api"
    }

def route_crawl(row: pd.Series) -> dict:
    url = row["urls"]
    t = row["type"]

    try:
        if t == "static_text":
            data = crawl_static_text(url)
        elif t == "static_table":
            data = crawl_static_table(url)
        elif t == "json_api":
            data = crawl_json_api(url)
        elif t == "dynamic":
            data = {
                "url": url,
                "title": "",
                "content": "",
                "status": "deferred",
                "type": "dynamic"
            }
        else:
            data = {
                "url": url,
                "title": "",
                "content": "",
                "status": "unknown_type",
                "type": "unknown"
            }

        data["source"] = row.get("source", "")
        data["timestamp"] = datetime.now().isoformat()
        return data

    except Exception as e:
        return {
            "url": url,
            "source": row.get("source", ""),
            "type": t,
            "title": "",
            "content": "",
            "status": f"error: {e}",
            "timestamp": datetime.now().isoformat()
        }

def save_jsonl(results: list, filename: str):
    """保存为 JSONL 格式（每行一个 JSON）"""
    with open(filename, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def save_md(results: list, filename: str):
    """保存为 Markdown 格式"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Immigration Policy Documents\n\n")
        for r in results:
            f.write(f"## {r.get('title', 'Untitled')}\n\n")
            f.write(f"**Source:** {r['source']} | **URL:** {r['url']}\n\n")
            if r.get("content"):
                f.write(f"{r['content']}\n\n")
            if r.get("tables"):
                f.write("### Tables\n\n")
                for t in r["tables"]:
                    f.write(f"```\n{t}\n```\n\n")
            if r.get("jsonld"):
                f.write("### Structured Data\n\n")
                f.write(f"```json\n{json.dumps(r['jsonld'], ensure_ascii=False, indent=2)}\n```\n\n")
            f.write("---\n\n")

def main():
    df = pd.read_csv("url_type_results.csv")
    df = df.dropna(subset=["urls", "type"]).drop_duplicates(subset=["urls"]).reset_index(drop=True)

    results = []
    total = len(df)
    
    for i, row in df.iterrows():
        print(f"[{i+1}/{total}] {row['type']} -> {row['urls']}")
        results.append(route_crawl(row))
        time.sleep(0.1)

    # 保存为 JSONL（便于 RAG 逐行读取和向量化）
    save_jsonl(results, "crawl_results.jsonl")
    
    # 保存为 Markdown（便于人工审阅）
    save_md(results, "crawl_results.md")

    # dynamic 单独导出
    dynamic_df = df[df["type"] == "dynamic"][["urls", "source", "type"]]
    dynamic_df.to_csv("dynamic_queue.csv", index=False, encoding="utf-8-sig")

    print("Done: crawl_results.jsonl, crawl_results.md, dynamic_queue.csv")

if __name__ == "__main__":
    main()