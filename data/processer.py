import json

with open("codeforces.json", "r", encoding='utf-8') as f:
    data = json.load(f)

ans = {}

for problem in data["result"]["problems"]:
    try:
        rating = problem["rating"]
    except KeyError:
        continue
    try:
        ans[rating].append({
            "pid": f"{problem['contestId']}{problem['index']}",
            "name": problem['name'],
            "url": f"https://codeforces.com/contest/{problem['contestId']}/problem/{problem['index']}"
        })
    except KeyError:
        ans[rating] = [
            {
                "pid": f"{problem['contestId']}{problem['index']}",
                "name": problem['name'],
                "url": f"https://codeforces.com/contest/{problem['contestId']}/problem/{problem['index']}"
            }
        ]

with open("cfrate.json", "w", encoding='utf-8') as f:
    json.dump(ans, f)
