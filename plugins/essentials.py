import json
import random
import miraicle
import requests


@miraicle.Mirai.receiver('GroupMessage')
def essentials(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message = str(msg.plain).split(" ")
    if message[0] == "/essentials":
        bot.send_group_msg(group=msg.group, msg=[
            miraicle.Plain("/hello - Hello, world!\n"),
            miraicle.Plain("/test - 测试网络连通性\n"),
            miraicle.Plain("/about - 关于\n"),
            miraicle.Plain("/help - 帮助\n")
        ], quote=msg.id)
    if message[0] == "/hello":
        bot.send_group_msg(group=msg.group, msg=[
            miraicle.Plain("Hello, world!"),
        ], quote=msg.id)
    if message[0] == "/test":
        ret = "# 网络测试\n"
        try:
            requests.get("https://www.luogu.com.cn")
            ret += "洛谷 | OK\n"
        except:
            ret += "洛谷 | ERROR\n"
        try:
            requests.get("https://www.codeforces.com")
            ret += "Codeforces | OK\n"
        except:
            ret += "Codeforces | ERROR\n"
        ret += "\n# 随机数测试\n"
        ret += "1-10000: " + str(random.randint(1, 10000)) + "\n"
        ret += "\n测试完成"
        bot.send_group_msg(group=msg.group, msg=[
            miraicle.Plain(ret),
        ], quote=msg.id)
    if message[0] == "/about":
        bot.send_group_msg(group=msg.group, msg=[
            miraicle.Plain("Surise Bot Core v20231029 by CodeZhangBorui"),
        ], quote=msg.id)