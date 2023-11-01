import miraicle
import requests


@miraicle.Mirai.receiver('GroupMessage')
def gpt_plug(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message = str(msg.plain).split(" ")
    if message[0] == "/gpt_plug":
        bot.send_group_msg(group=msg.group, msg=[
            miraicle.Plain("键入 “> 问题” 开始向 GPT 提问")
        ], quote=msg.id)
    if message[0] != '>':
        return
    question = ""
    for mess in message[1:]:
        question += mess + " "
    print(f"Fetching response of ChatGPT: {question}")
    url = "https://freegptapi.gestar.cloud/?msg=" + question
    bot.send_group_msg(group=msg.group, msg=[
        miraicle.Plain("\n" + requests.get(url).text),
    ], quote=msg.id)
