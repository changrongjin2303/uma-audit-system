#!/usr/bin/env python3
import random
import sys
import time
from typing import Dict, List, Optional

import json
import urllib.request
import urllib.parse


API_BASE = "http://localhost:8000"
PAGE_SIZE = 200

PROJECT_TYPES = [
    "建筑工程",
    "装修工程",
    "市政工程",
    "园林工程",
    "公路工程",
    "其他工程",
]


def http_get(url: str) -> Dict:
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_patch(url: str, data: Dict) -> Dict:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_projects() -> List[Dict]:
    page = 1
    items: List[Dict] = []
    while True:
        url = f"{API_BASE}/projects?page={page}&size={PAGE_SIZE}"
        data = http_get(url)
        # 兼容两种结构：{data:{items,total}} 或 {items,total}
        payload = data.get("data", data)
        page_items = payload.get("items", [])
        total = payload.get("total", 0)
        items.extend(page_items)
        if len(items) >= total or not page_items:
            break
        page += 1
    return items


def main():
    print("Fetching projects...")
    projects = fetch_all_projects()
    print(f"Total projects: {len(projects)}")

    to_update = [p for p in projects if not p.get("type")]
    print(f"Projects without type: {len(to_update)}")

    stats = {t: 0 for t in PROJECT_TYPES}
    updated = 0
    for p in to_update:
        t = random.choice(PROJECT_TYPES)
        pid = p.get("id")
        try:
            http_patch(f"{API_BASE}/projects/{pid}", {"type": t})
            stats[t] += 1
            updated += 1
        except Exception as e:
            print(f"Failed to update project {pid}: {e}")

    print("\nAssignment summary:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"\nUpdated projects: {updated}")
    print("Done.")


if __name__ == "main__":
    main()

if __name__ == "__main__":
    main()

