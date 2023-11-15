# Generate lgrate.json from luogu.com.cn

import json
import time

import requests
import math

DefaultUA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57"

with open("../config/luogu.json", "r", encoding="utf-8") as f:
    LoginCredit = json.load(f)["account"]

preload = requests.get(
    f"https://www.luogu.com.cn/problem/list",
    headers={
        "User-Agent": DefaultUA,
        "x-luogu-type": "content-only"
    },
    cookies=LoginCredit,
).json()

pages = math.ceil(preload["currentData"]["problems"]["count"] / 50)
print(f"Total {pages} pages")

output = {}

for page in range(1, pages + 1):
    data = requests.get(
        f"https://www.luogu.com.cn/problem/list?page={page}",
        headers={
            "User-Agent": DefaultUA,
            "x-luogu-type": "content-only"
        },
        cookies=LoginCredit,
    ).json()
    for problem in data["currentData"]["problems"]["result"]:
        try:
            rating = str(problem["difficulty"])
        except KeyError:
            continue
        try:
            output[rating].append({
                "pid": problem['pid'],
                "name": problem['title'],
                "url": f"https://www.luogu.com.cn/problem/{problem['pid']}"
            })
        except KeyError:
            output[rating] = [
                {
                    "pid": problem['pid'],
                    "name": problem['title'],
                    "url": f"https://www.luogu.com.cn/problem/{problem['pid']}"
                }
            ]
    print(f"Page {page} done")
    time.sleep(0.1)

with open("lgrate.json", "w", encoding='utf-8') as f:
    json.dump(output, f)
