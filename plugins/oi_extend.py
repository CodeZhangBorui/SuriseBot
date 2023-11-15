import json
import math
import random
import time

import colorama
import miraicle
import requests

# Ignore proxy
requests = requests.Session()
requests.trust_env = False

# Define global variables and load data
DefaultUA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57"
ProcessLocker = False
TodayLocker = {
    "status": False,
    "timestamp": 0,
}

with open("config/luogu.json", "r", encoding="utf-8") as f:
    LoginCredit = json.load(f)["account"]

with open("data/accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

with open("data/duel.json", "r", encoding="utf-8") as f:
    duelPool = json.load(f)["duelPool"]

with open("data/rating.json", "r", encoding="utf-8") as f:
    rating = json.load(f)

with open("config/admin.json", "r", encoding='utf-8') as f:
    admin = json.load(f)["list"]


# Define basic functions
def log(msg, end='\n'):
    print(f"{colorama.Fore.YELLOW}{msg}{colorama.Style.RESET_ALL}", end=end)


def get_today_timestamp():
    import time
    return int(time.time()) - int(time.time()) % 86400 - 28000


def get_record_list(uid, pid=None):
    log(f"Getting record list of {uid}", end="")
    if pid is None:
        url = f"https://www.luogu.com.cn/record/list?user={uid}"
    else:
        url = f"https://www.luogu.com.cn/record/list?user={uid}&pid={pid}"
        log(f" for {pid}", end="")
    rlist = []
    for i in range(3):
        try:
            res = requests.get(
                f"{url}&page={i + 1}",
                headers={
                    "User-Agent": DefaultUA,
                    "x-luogu-type": "content-only"
                },
                cookies=LoginCredit,
            ).json()
        except:
            log(f"Failed to get [{url}&page={i + 1}], page not found?")
            res = {"currentData": {"records": {"result": []}}}
        rlist.extend(res["currentData"]["records"]["result"])
    log(f" | OK {len(rlist)} record(s)")
    return rlist


def elo_rating(ra, rb, sa):
    k = 128
    ea = 1 / (1 + 10 ** ((rb - ra) / 400))
    ra_ = ra + k * (sa - ea)
    return ra_


def rlist_unique(rlist):
    log("Unique and filter AC records", end="")
    unique = []
    seen_pids = set()
    for item in rlist:
        if item["status"] == 12 and item["problem"]["pid"] not in seen_pids:
            seen_pids.add(item["problem"]["pid"])
            unique.append(item)
    log(f" | OK {len(unique)} record(s)")
    return unique


def get_counterpart(sender, duel):
    return duel["receiver"] if sender == duel["sender"] else duel["sender"]


def reload_all():
    global accounts, duelPool, rating, admin
    with open(r"data/accounts.json", "r", encoding="utf-8") as f:
        accounts = json.load(f)
    with open(r"data/duel.json", "r", encoding="utf-8") as f:
        duelPool = json.load(f)["duelPool"]
    with open(r"data/rating.json", "r", encoding="utf-8") as f:
        rating = json.load(f)
    with open(r"config/admin.json", "r", encoding='utf-8') as f:
        admin = json.load(f)["list"]


def randomproblem(inrating):
    if int(inrating) < 100:
        with open(r"data/lgrate.json", "r", encoding="utf-8") as f:
            return random.choice(json.load(f)[inrating])
    else:
        with open(r"data/cfrate.json", "r", encoding="utf-8") as f:
            return random.choice(json.load(f)[inrating])


def genreport(uselocker=True):
    today = get_today_timestamp()
    diff2points = [3, 0, 1, 2, 3, 5, 7, 10]
    now = 0
    allpoints = {}
    for qq in accounts:
        rlist = get_record_list(accounts[qq])
        tot = 0
        points = 0
        rlist = rlist_unique(rlist)
        for record in rlist:
            if record["submitTime"] < today:
                break
            if TodayLocker["status"] is True and record["submitTime"] > TodayLocker["timestamp"] and uselocker is True:
                continue
            if record["problem"]["type"] == "U" or record["problem"]["type"] == "T":
                continue
            points += diff2points[record["problem"]["difficulty"]]
            tot += 1
        allpoints[qq] = points
        now += 1
        log(f"Report generating | {now}/{len(accounts)} ({math.floor(now / len(accounts) * 100)}%)")
    rank = sorted(allpoints.items(), key=lambda x: x[1], reverse=True)
    log(f"Report generated | OK {time.strftime('%m-%d %H:%M', time.localtime())} ({len(rank)} users)")
    ret = "今日做题情况报告：\n"
    if TodayLocker["status"]:
        if uselocker is True:
            ret += f"报告生成时间：{time.strftime('%m-%d %H:%M', time.localtime(TodayLocker['timestamp']))}（已封榜）\n\n"
        else:
            ret += f"报告生成时间：{time.strftime('%m-%d %H:%M', time.localtime(TodayLocker['timestamp']))}（忽略封榜）\n\n"
    else:
        ret += f"报告生成时间：{time.strftime('%m-%d %H:%M', time.localtime())}\n\n"
    now = 1
    valid = 0
    for rk in rank:
        if rk[1] == 0:
            break
        else:
            if now == 1:
                ret += f"{now} | {accounts[rk[0]]} | {rk[1]} 🥇\n"
            elif now == 2:
                ret += f"{now} | {accounts[rk[0]]} | {rk[1]} 🥈\n"
            elif now == 3:
                ret += f"{now} | {accounts[rk[0]]} | {rk[1]} 🥉\n"
            else:
                ret += f"{now} | {accounts[rk[0]]} | {rk[1]}\n"
        now += 1
        valid += 1
    if valid == 0:
        ret += "今日没有人做题"
    elif valid < len(accounts):
        ret += f"\n还有 {len(accounts) - valid} 人没有做题"
    return ret


def gentoday(qq):
    if str(qq) not in accounts:
        return "你还没有绑定账号，输入 /duel bind <洛谷用户名> 绑定账号"
    today = get_today_timestamp()
    rlist = get_record_list(accounts[str(qq)])
    ret = f"{accounts[str(qq)]} 的今日做题情况：\n"
    if TodayLocker["status"]:
        ret += f"报告生成时间：{time.strftime('%m-%d %H:%M', time.localtime(TodayLocker['timestamp']))}（已封榜）\n\n"
    else:
        ret += f"报告生成时间：{time.strftime('%m-%d %H:%M', time.localtime())}\n\n"
    tot = 0
    diffs = [
        "暂未评定",
        "入门",
        "普及-",
        "普及/提高-",
        "普及+/提高",
        "提高+/省选-",
        "省选/NOI-",
        "NOI/NOI+/CTSC",
    ]
    diff2points = [3, 0, 1, 2, 3, 5, 7, 10]
    points = 0
    rlist = rlist_unique(rlist)
    for record in rlist:
        if record["submitTime"] < today:
            break
        if TodayLocker["status"] is True and record["submitTime"] > TodayLocker["timestamp"]:
            continue
        if record["problem"]["type"] == "U" or record["problem"]["type"] == "T":
            continue
        ret += f"通过 {record['problem']['pid']} | 难度 {diffs[record['problem']['difficulty']]} | +{diff2points[record['problem']['difficulty']]}\n"
        points += diff2points[record["problem"]["difficulty"]]
        tot += 1
    if tot == 0:
        ret += "今日没有通过任何题目"
    else:
        ret += f"今日共通过 {tot} 题，积分 {points}"
    return ret


# Define modules
def do_duel(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    msgchain = msg.plain.split(" ")
    if len(msgchain) == 1:
        bot.send_group_msg(
            group=msg.group,
            msg="OI-Extend Duel Module v1.2.1\n键入 /duel begin @user rating 开始对战",
        )
        return
    if msgchain[1] in ["bind"]:
        if len(msgchain) < 3:
            bot.send_group_msg(group=msg.group, msg="参数错误：/duel bind <洛谷 UID>")
            return
        log(f"Binding @{msg.sender} to {msgchain[2]}", end="")
        res = requests.get(
            f"https://www.luogu.com.cn/user/{msgchain[2]}",
            headers={"User-Agent": DefaultUA, "x-luogu-type": "content-only"},
        ).json()
        if str(res["currentData"]["user"]["introduction"]).startswith(str(msg.sender)):
            accounts[str(msg.sender)] = res["currentData"]["user"]["name"]
            with open(r"data/accounts.json", "w", encoding="utf-8") as f:
                json.dump(accounts, f)
            if str(msg.sender) not in rating:
                rating[str(msg.sender)] = 1400
                with open(r"data/rating.json", "w", encoding="utf-8") as f:
                    json.dump(rating, f)
            log(f" | OK Username is {res['currentData']['user']['name']}")
            bot.send_group_msg(
                group=msg.group,
                msg="绑定成功，你的洛谷用户名为 " + res["currentData"]["user"]["name"],
            )
        else:
            log(f" | Unaccepted user introduction:\n{res['currentData']['user']['introduction']}")
            bot.send_group_msg(
                group=msg.group,
                msg=f"你正在绑定账号 {msgchain[2]}，请在个人介绍开头处顶格填入你的 QQ 号，然后再次输入 /duel bind <洛谷 UID> 完成绑定。绑定完成后，你可以将添加的 QQ 号删除。",
            )
        return
    if msgchain[1] in ["list", "ls", "lis", "lt"]:
        log(f"Listing duel pool | OK {len(duelPool)} Duel(s)")
        ret = "当前正在进行的对战：\n\n"
        now = time.time()
        for duel in duelPool:
            hours = int((now - duel["timestamp"]) / 3600)
            minutes = int((now - duel["timestamp"]) / 60 - hours * 60)
            if duel["status"] == 1:
                ret += f"{accounts[str(duel['sender'])]} vs {accounts[str(duel['receiver'])]} | Rating {duel['rating']} | 等待对方接受...\n"
            elif duel["status"] == 2:
                ret += f"{accounts[str(duel['sender'])]} vs {accounts[str(duel['receiver'])]} | Rating {duel['rating']} | {duel['problem']['pid']} | 已用时：{hours}小时 {minutes}分钟\n"
            elif duel["status"] == 3:
                ret += f"{accounts[str(duel['sender'])]} vs {accounts[str(duel['receiver'])]} | Rating {duel['rating']} | {duel['problem']['pid']} (等待对方同意更换题目) | 已用时：{hours}小时 {minutes}分钟\n"
        bot.send_group_msg(group=msg.group, msg=ret)
        return
    if msgchain[1] in ["rank", "rk", "rak"]:
        log(f"Listing duel rank | OK {len(rating)} Rating(s)")
        rank = sorted(rating.items(), key=lambda x: x[1], reverse=True)
        ret = "Duel Rating 排行榜：\n"
        now = 1
        for rk in rank:
            ret += f"{now} | Rating {rk[1]} | {accounts[rk[0]]}\n"
            now += 1
        bot.send_group_msg(group=msg.group, msg=ret)
    if msgchain[1] in ["problem"]:
        if len(msgchain) != 3:
            bot.send_group_msg(group=msg.group, msg="参数错误：/duel problem <Rating>")
            return
        if not (
                (int(msgchain[2]) % 100 == 0
                 and 800 <= int(msgchain[2]) <= 3500)
                or
                (
                        0 <= int(msgchain[2]) <= 7
                )
        ):
            bot.send_group_msg(group=msg.group, msg="Rating 需为 800 到 3500 的整百数（Codeforces）或 0-7（洛谷）")
            return
        problem = randomproblem(msgchain[2])
        log(f"Choose a problem for @{msg.sender} | OK {problem['name']}")
        bot.send_group_msg(
            group=msg.group,
            msg=[
                miraicle.Plain(
                    f"{problem['pid']} : {problem['name']}\n快捷前往：{problem['url']}"
                ),
            ],
        )
    if msgchain[1] in ["begin", "bg", "beg", "begi", "bgi"]:
        if len(msgchain) != 4:
            bot.send_group_msg(group=msg.group, msg="参数错误：/duel begin @user rating")
            return
        if len(msgchain) < 2 or type(msg.chain[1]) != miraicle.message.At:
            bot.send_group_msg(group=msg.group, msg="你需要 @对方 来开始对战")
            return
        if not (
                (int(msgchain[3]) % 100 == 0
                 and 800 <= int(msgchain[3]) <= 3500)
                or
                (
                        0 <= int(msgchain[3]) <= 7
                )
        ):
            bot.send_group_msg(group=msg.group, msg="Rating 需为 800 到 3500 的整百数（Codeforces）或 0-7（洛谷）")
            return
        for duel in duelPool:
            if duel["sender"] == msg.sender or duel["receiver"] == msg.sender:
                bot.send_group_msg(
                    group=msg.group, msg="你已经在进行对战了，要想开始新的对战，你需要输入 /duel giveup 放弃当前对战"
                )
                return
        if msg.sender == msg.chain[1].qq:
            bot.send_group_msg(group=msg.group, msg=miraicle.Image.from_base64(
                base64='images/418_im_a_teapot.jpg'
            ))
            bot.send_group_msg(group=msg.group, msg="你不能 Duel 你自己")
            return
        if not str(msg.sender) in accounts:
            bot.send_group_msg(
                group=msg.group, msg="你还没有绑定账号，输入 /duel bind <洛谷用户名> 绑定账号"
            )
            return
        if not str(msg.chain[1].qq) in accounts:
            bot.send_group_msg(
                group=msg.group, msg="对方还没有绑定账号，输入 /duel bind <洛谷 UID> 绑定账号"
            )
            return
        problem = randomproblem(msgchain[2])
        log(f"Choose a problem for the new duel:\n{problem}")
        duel = {
            "sender": msg.sender,
            "receiver": msg.chain[1].qq,
            "problem": problem,
            "rating": int(msgchain[3]),
            "timestamp": int(time.time()),
            "status": 1,
        }
        duelPool.append(duel)
        with open(r"data/duel.json", "w", encoding="utf-8") as f:
            json.dump({"duelPool": duelPool}, f)
        log(
            f"New duel invitation created:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}")
        bot.send_group_msg(
            group=msg.group,
            msg=[
                miraicle.At(duel["receiver"]),
                miraicle.Plain("，你收到了来自 "),
                miraicle.At(duel["sender"]),
                miraicle.Plain(" 的挑战，同意请输入 /duel accept，拒绝请输入 /duel reject"),
            ],
        )
    if msgchain[1] in ["accept"]:
        for duel in duelPool:
            if duel["receiver"] == msg.sender and duel["status"] == 1:
                log(
                    f"Duel accepted:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}")
                duel["status"] = 2
                duel["timestamp"] = int(time.time())
                with open(r"data/duel.json", "w", encoding="utf-8") as f:
                    json.dump({"duelPool": duelPool}, f)
                bot.send_group_msg(
                    group=msg.group,
                    msg=[
                        miraicle.Plain(
                            f"对战开始，题目为 {duel['problem']['pid']}\n快捷前往：{duel['problem']['url']}\n结算请使用 /duel judge"
                        ),
                    ],
                )
                return
        bot.send_group_msg(group=msg.group, msg="你没有收到挑战")
    if msgchain[1] in ["reject"]:
        for duel in duelPool:
            if duel["receiver"] == msg.sender and duel["status"] == 1:
                log(
                    f"Duel rejected:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}")
                duelPool.remove(duel)
                with open(r"data/duel.json", "w", encoding="utf-8") as f:
                    json.dump({"duelPool": duelPool}, f)
                bot.send_group_msg(
                    group=msg.group,
                    msg=[
                        miraicle.Plain("已拒绝对战"),
                    ],
                )
                return
        bot.send_group_msg(group=msg.group, msg="你没有收到挑战")
    if msgchain[1] in ["judge"]:
        for duel in duelPool:
            if (
                    msg.sender == duel["sender"] or msg.sender == duel["receiver"]
            ) and duel["status"] != 1:
                records = get_record_list(
                    accounts[str(msg.sender)], "CF" + duel["problem"]["pid"]
                )
                for record in records:
                    if record["submitTime"] < duel["timestamp"]:
                        break
                    if record["status"] == 12:
                        elo_a = int(
                            elo_rating(
                                rating[str(msg.sender)],
                                rating[str(get_counterpart(msg.sender, duel))],
                                1,
                            )
                        )
                        elo_b = int(
                            elo_rating(
                                rating[str(get_counterpart(msg.sender, duel))],
                                rating[str(msg.sender)],
                                0,
                            )
                        )
                        duelPool.remove(duel)
                        with open(r"data/duel.json", "w", encoding="utf-8") as f:
                            json.dump({"duelPool": duelPool}, f)
                        now = time.time()
                        hours = int((now - duel["timestamp"]) / 3600)
                        minutes = int((now - duel["timestamp"]) / 60 - hours * 60)
                        log(
                            f"Duel finished:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}\nTime: {hours}h {minutes}m\nRating: {elo_a} | {elo_b}")
                        bot.send_group_msg(
                            group=msg.group,
                            msg=[
                                miraicle.Plain(f"对战结束（用时 {hours}小时 {minutes}分钟），"),
                                miraicle.At(int(msg.sender)),
                                miraicle.Plain(
                                    f"的 Rating 为 {elo_a} (+{elo_a - rating[str(duel['sender'])]})，"
                                ),
                                miraicle.At(int(get_counterpart(msg.sender, duel))),
                                miraicle.Plain(
                                    f"的 Rating 为 {elo_b} (-{rating[str(duel['receiver'])] - elo_b})"
                                ),
                            ],
                        )
                        rating[str(msg.sender)] = elo_a
                        rating[str(get_counterpart(msg.sender, duel))] = elo_b
                        with open(r"data/rating.json", "w", encoding="utf-8") as f:
                            json.dump(rating, f)
                        return
                bot.send_group_msg(group=msg.group, msg="没有找到有关此题的 AC 记录。")
                return
        bot.send_group_msg(group=msg.group, msg="你没有正在进行的对战")
        return
    if msgchain[1] in ["change"]:
        if len(msgchain) >= 3:
            for duel in duelPool:
                if (
                        duel["sender"] == msg.sender or duel["receiver"] == msg.sender
                ) and duel["status"] == 3:
                    if duel["operator"] == msg.sender:
                        bot.send_group_msg(group=msg.group, msg="你不能接受自己的更换题目申请")
                        return
                    if msgchain[2] == "accept":
                        problem = randomproblem(msgchain[2])
                        duel["problem"] = problem
                        duel["status"] = 2
                        duel["timestamp"] = int(time.time())
                        duel.remove("operator")
                        with open(r"data/duel.json", "w", encoding="utf-8") as f:
                            json.dump({"duelPool": duelPool}, f)
                        log(
                            f"New problem for the duel:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}")
                        bot.send_group_msg(
                            group=msg.group,
                            msg=[
                                miraicle.Plain(
                                    f"重新选题成功，题目为 {duel['problem']['pid']}\n快捷前往：https://www.luogu.com.cn/problem/CF{duel['problem']['pid']}\n结算请使用 /duel judge"
                                ),
                            ],
                        )
                        return
                    if msgchain[2] == "reject":
                        duel["status"] = 2
                        duel.remove("operator")
                        with open(r"data/duel.json", "w", encoding="utf-8") as f:
                            json.dump({"duelPool": duelPool}, f)
                        bot.send_group_msg(group=msg.group, msg="已拒绝更换题目")
                        return
            bot.send_group_msg(group=msg.group, msg="你没有正在进行的对战")
            return
        for duel in duelPool:
            if duel["sender"] == msg.sender or duel["receiver"] == msg.sender:
                if duel["status"] == 2 or duel["status"] == 4:
                    duel["status"] = 3
                    duel["operator"] = msg.sender
                    bot.send_group_msg(
                        group=msg.group, msg="更换题目申请已发送，请对方键入 /duel change accept 同意换题"
                    )
                    return
                elif duel["status"] == 1:
                    bot.send_group_msg(group=msg.group, msg="对方还没有接受对战")
                    return
                elif duel["status"] == 3:
                    bot.send_group_msg(
                        group=msg.group,
                        msg="你已经申请过更换题目了，请对方输入 /duel change accept 同意换题",
                    )
                    return
        bot.send_group_msg(group=msg.group, msg="你没有正在进行的对战")
        return
    if msgchain[1] in ["giveup"]:
        for duel in duelPool:
            if duel["sender"] == msg.sender or duel["receiver"] == msg.sender:
                log(
                    f"Duel given up:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}")
                duelPool.remove(duel)
                with open(r"data/duel.json", "w", encoding="utf-8") as f:
                    json.dump({"duelPool": duelPool}, f)
                rating[str(msg.sender)] = int(
                    elo_rating(
                        rating[str(msg.sender)],
                        rating[str(get_counterpart(msg.sender, duel))],
                        0,
                    )
                )
                with open(r"data/rating.json", "w", encoding="utf-8") as f:
                    json.dump(rating, f)
                bot.send_group_msg(
                    group=msg.group,
                    msg=f"已放弃对战，Rating 更改为 {str(rating[str(msg.sender)])}",
                )
                return
        bot.send_group_msg(group=msg.group, msg="你没有正在进行的对战")
        return
    if msgchain[1] in ["cancel"]:
        if len(msgchain) >= 3:
            for duel in duelPool:
                if (
                        duel["sender"] == msg.sender or duel["receiver"] == msg.sender
                ) and duel["status"] == 4:
                    if duel["operator"] == msg.sender:
                        bot.send_group_msg(group=msg.group, msg="你不能取消自己发起的取消申请")
                        return
                    if msgchain[2] == "accept":
                        log(
                            f"Duel canceled:\nSender | Receiver : {duel['sender']} | {duel['receiver']}\nProblem: {duel['problem']}")
                        duelPool.remove(duel)
                        with open(r"data/duel.json", "w", encoding="utf-8") as f:
                            json.dump({"duelPool": duelPool}, f)
                        bot.send_group_msg(
                            group=msg.group,
                            msg="取消 Duel 成功，Rating 不变",
                        )
                        return
                    if msgchain[2] == "reject":
                        duel["status"] = 2
                        duel.remove("operator")
                        with open(r"data/duel.json", "w", encoding="utf-8") as f:
                            json.dump({"duelPool": duelPool}, f)
                        bot.send_group_msg(group=msg.group, msg="已拒绝取消 Duel")
                        return
            bot.send_group_msg(group=msg.group, msg="你没有正在进行的对战")
            return
        for duel in duelPool:
            if duel["sender"] == msg.sender or duel["receiver"] == msg.sender:
                if duel["status"] == 2 or duel["status"] == 3:
                    duel["status"] = 4
                    duel["operator"] = msg.sender
                    bot.send_group_msg(
                        group=msg.group, msg="取消申请已发送，请对方键入 /duel cancel accept 同意取消"
                    )
                    return
                elif duel["status"] == 1:
                    bot.send_group_msg(group=msg.group, msg="对方还没有接受对战")
                    return
                elif duel["status"] == 4:
                    bot.send_group_msg(
                        group=msg.group,
                        msg="你已经申请过更换题目了，请对方输入 /duel change accept 同意换题",
                    )
                    return
        bot.send_group_msg(group=msg.group, msg="你没有正在进行的对战")
        return


def do_today_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    msgchain = msg.plain.split(" ")
    if len(msgchain) < 2:
        bot.send_group_msg(
            group=msg.group,
            msg="OI-Extend Today Module v1.0.0\n键入 /today @群成员 获取群成员今日做题情况",
        )
        return
    if msgchain[1] in ["lock"]:
        if msg.sender not in admin:
            bot.send_group_msg(group=msg.group, msg="权限不足")
            return
        log(f"Locking today's report | OK {time.strftime('%m-%d %H:%M', time.localtime())}")
        TodayLocker["status"] = True
        TodayLocker["timestamp"] = int(time.time())
        bot.send_group_msg(group=msg.group, msg="封榜操作成功")
        return
    if msgchain[1] in ["unlock"]:
        if msg.sender not in admin:
            bot.send_group_msg(group=msg.group, msg="权限不足")
            return
        log(f"Unlocking today's report | OK")
        TodayLocker["status"] = False
        bot.send_group_msg(group=msg.group, msg="解除封榜操作成功")
        return
    if msgchain[1] in ["report", "rp"]:
        global ProcessLocker
        ProcessLocker = True
        try:
            bot.send_group_msg(group=msg.group, msg="正在生成报告，大约需要 30 秒甚至更久，请稍后...")
            ret = genreport()
            bot.send_group_msg(group=msg.group, msg=ret)
        except Exception as e:
            bot.send_group_msg(group=msg.group, msg=miraicle.Image.from_base64(
                base64='images/504_gateway_timeout.jpg'
            ))
            bot.send_group_msg(group=msg.group, msg="生成报告失败")
            print("")
            log(e)
        ProcessLocker = False
        return
    if type(msg.chain[1]) != miraicle.message.At:
        bot.send_group_msg(
            group=msg.group,
            msg="OI-Extend Today Module v1.0.0\n键入 /today @群成员 获取群成员今日做题情况",
        )
        return
    ret = gentoday(msg.chain[1].qq)
    bot.send_group_msg(group=msg.group, msg=ret)


def do_today_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    msgchain = msg.plain.split(" ")
    if len(msgchain) > 2:
        bot.send_friend_msg(
            qq=msg.sender,
            msg="OI-Extend Today Module v1.0.0\n键入 /today report 获取所有人今日做题情况",
        )
        return
    if len(msgchain) < 2:
        ret = gentoday(msg.sender)
        bot.send_friend_msg(qq=msg.sender, msg=ret)
        return
    if msgchain[1] in ["lock"]:
        if msg.sender not in admin:
            bot.send_friend_msg(qq=msg.sender, msg="权限不足")
            return
        log(f"Locking today's report | OK {time.strftime('%m-%d %H:%M', time.localtime())}")
        TodayLocker["status"] = True
        TodayLocker["timestamp"] = int(time.time())
        bot.send_friend_msg(qq=msg.sender, msg="封榜操作成功")
        return
    if msgchain[1] in ["unlock"]:
        if msg.sender not in admin:
            bot.send_friend_msg(qq=msg.sender, msg="权限不足")
            return
        log(f"Unlocking today's report | OK")
        TodayLocker["status"] = False
        bot.send_friend_msg(qq=msg.sender, msg="解除封榜操作成功")
        return
    if msgchain[1] in ["report", "rp"]:
        global ProcessLocker
        ProcessLocker = True
        if len(msgchain) == 3 and msgchain[2] in ["force"]:
            bot.send_friend_msg(qq=msg.sender, msg="忽略封榜状态……")
            uselocker = False
        else:
            uselocker = True
        try:
            bot.send_friend_msg(qq=msg.sender, msg="正在生成报告，大约需要 30 秒甚至更久，请稍后...")
            ret = genreport(uselocker)
            bot.send_friend_msg(qq=msg.sender, msg=ret)
        except Exception as e:
            bot.send_friend_msg(qq=msg.sender, msg=miraicle.Image.from_base64(
                base64='images/504_gateway_timeout.jpg'
            ))
            bot.send_friend_msg(qq=msg.sender, msg="生成报告失败")
            print("")
            log(e)
        ProcessLocker = False
        return
    if len(msg.chain) < 2 or type(msg.chain[1]) != miraicle.message.At:
        bot.send_friend_msg(
            qq=msg.sender,
            msg="OI-Extend Today Module v1.0.0 (Friend Mode)\n键入 /today report 获取所有人今日做题情况",
        )
        return


log(f"OI-Extend Loaded")
log(f"Login via uid {LoginCredit['_uid']} client_id {LoginCredit['__client_id']}")


@miraicle.Mirai.receiver("GroupMessage")
def oi_extend(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    if not msg.plain.startswith("/"):
        return
    msgchain = msg.plain.split(" ")
    log(f"Proceed Command:{msgchain}")
    if msgchain[0] == "/oi_extend":
        if len(msgchain) < 2:
            bot.send_group_msg(
                group=msg.group,
                msg="/duel - OI-Extend Duel Module v1.2.1\n/today - OI-Extend Today Module v1.0.0",
                quote=msg.id,
            )
            return
        if msgchain[1] == "reload":
            # Reload all data and config from files
            reload_all()
            bot.send_group_msg(
                group=msg.group,
                msg="已重新加载所有数据和配置",
            )
    if msgchain[0] in ["/duel"]:
        do_duel(bot, msg)
    if msgchain[0] in ["/today", "/td", "/tod"]:
        if ProcessLocker is True:
            bot.send_group_msg(group=msg.group, msg="正在处理一个任务，请等待任务完成后重试")
            return
        do_today_group(bot, msg)


@miraicle.Mirai.receiver("FriendMessage")
def oi_extend_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    if not msg.plain.startswith("/"):
        return
    msgchain = msg.plain.split(" ")
    log(f"Proceed Command:{msgchain}")
    if msgchain[0] == "/oi_extend":
        if len(msgchain) < 2:
            bot.send_friend_msg(
                qq=msg.sender,
                msg="/duel - OI-Extend Duel Module v1.2.1\n/today - OI-Extend Today Module v1.0.0",
            )
            return
        if msgchain[1] == "reload":
            # Reload all data and config from files
            reload_all()
            bot.send_friend_msg(
                qq=msg.sender,
                msg="已重新加载所有数据和配置",
            )
    if msgchain[0] in ["/today", "/td", "/tod"]:
        if ProcessLocker is True:
            bot.send_friend_msg(qq=msg.sender, msg="正在处理一个任务，请等待任务完成后重试")
            return
        do_today_friend(bot, msg)
