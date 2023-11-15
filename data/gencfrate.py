# Generate cfrate.json from codeforces.com

import json
import requests

data = requests.get("https://codeforces.com/api/problemset.problems").json()

output = {}

for problem in data["result"]["problems"]:
    try:
        rating = problem["rating"]
    except KeyError:
        continue
    try:
        output[rating].append({
            "pid": f"{problem['contestId']}{problem['index']}",
            "name": problem['name'],
            "url": f"https://www.luogu.com.cn/problem/CF{problem['contestId']}{problem['index']}"
        })
    except KeyError:
        output[rating] = [
            {
                "pid": f"{problem['contestId']}{problem['index']}",
                "name": problem['name'],
                "url": f"https://www.luogu.com.cn/problem/CF{problem['contestId']}{problem['index']}"
            }
        ]

with open("cfrate.json", "w", encoding='utf-8') as f:
    json.dump(output, f)
