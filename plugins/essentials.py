import json
import random
import miraicle
import requests

with open(r"config/admin.json", "r", encoding='utf-8') as f:
    admin = json.load(f)["list"]

with open(r"config/superadmin.json", "r", encoding='utf-8') as f:
    superadmin = json.load(f)["list"]

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
    if message[0] == "/admin":
        if msg.sender not in admin:
            bot.send_group_msg(group=msg.group, msg=[
                miraicle.Plain("权限不足"),
            ], quote=msg.id)
            return
        if len(message) < 2:
            bot.send_group_msg(group=msg.group, msg=[
                miraicle.Plain("参数错误：/admin <add|del> @member"),
            ])
        if message[1] == "list":
            ret = "管理员列表：\n"
            for i in admin:
                ret += f"- {i}\n"
            bot.send_group_msg(group=msg.group, msg=[
                miraicle.Plain(ret),
            ])
            return
        if len(message) < 3:
            bot.send_group_msg(group=msg.group, msg=[
                miraicle.Plain("参数错误：/admin <add|del> @member"),
            ])
        if message[1] == "add":
            if type(msg.chain[1]) != miraicle.message.At:
                bot.send_group_msg(group=msg.group, msg=[
                    miraicle.Plain("参数错误：/admin <add|del> @member"),
                ])
                return
            admin.append(msg.chain[1].qq)
            with open(r"config/admin.json", "w", encoding='utf-8') as f:
                json.dump({"list": admin}, f)
            bot.send_group_msg(group=msg.group, msg=[
                miraicle.Plain("添加管理员 "),
                miraicle.At(msg.chain[1].qq),
                miraicle.Plain(" 成功"),
            ])
            return
        if message[1] == "del":
            if type(msg.chain[1]) != miraicle.message.At:
                bot.send_group_msg(group=msg.group, msg=[
                    miraicle.Plain("参数错误：/admin <add|del> @member"),
                ])
                return
            if msg.chain[1].qq in superadmin:
                bot.send_group_msg(group=msg.group, msg=[
                    miraicle.Plain("无法删除此管理员：请编辑文件安全修改管理员"),
                ])
                return
            admin.remove(msg.chain[1].qq)
            with open(r"config/admin.json", "w", encoding='utf-8') as f:
                json.dump({"list": admin}, f)
            bot.send_group_msg(group=msg.group, msg=[
                miraicle.Plain("删除管理员 "),
                miraicle.At(msg.chain[1].qq),
                miraicle.Plain(" 成功"),
            ])
            return
    if message[0] == "/about":
        bot.send_group_msg(group=msg.group, msg=[
            miraicle.Plain("Surise Bot Core v20231029 by CodeZhangBorui"),
        ], quote=msg.id)