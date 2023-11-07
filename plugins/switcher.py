import json

import miraicle

with open(r"config/admin.json", "r", encoding='utf-8') as f:
    admin = json.load(f)["list"]


@miraicle.Mirai.filter('GroupSwitchFilter')
def switcher(bot: miraicle.Mirai, msg: miraicle.GroupMessage, flt: miraicle.GroupSwitchFilter):
    msgchain = msg.plain.split(' ')
    # if msgchain[0] == "/help":
    #     ret = ""
    #     for feature in flt.funcs_info(msg.group):
    #         if feature['enabled']:
    #             ret += f"- {feature['func']} (/{feature['func']})\n"
    #     bot.send_group_msg(
    #         group=msg.group,
    #         msg="已启用的模块列表：\n" + ret
    #     )
    if not msg.sender in admin:
        return
    if msgchain[0] == '/switcher':
        ret = ""
        if msgchain[1] == 'list':
            for feature in flt.funcs_info(msg.group):
                ret += f"{feature['func']}: {'开启' if feature['enabled'] else '关闭'}\n"
            bot.send_group_msg(
                group=msg.group,
                msg=ret
            )
        elif msgchain[1] == 'enable':
            if msgchain[2] == 'all':
                flt.enable_all(msg.group)
                bot.send_group_msg(
                    group=msg.group,
                    msg='已开启所有功能'
                )
            else:
                flt.enable(msg.group, msgchain[2])
                bot.send_group_msg(
                    group=msg.group,
                    msg='已开启功能 ' + msgchain[2]
                )
        elif msgchain[1] == 'disable':
            if msgchain[2] == 'all':
                flt.disable_all(msg.group)
                bot.send_group_msg(
                    group=msg.group,
                    msg='已关闭所有功能'
                )
            else:
                flt.disable(msg.group, msgchain[2])
                bot.send_group_msg(
                    group=msg.group,
                    msg='已关闭功能 ' + msgchain[2]
                )
        else:
            bot.send(msg, '参数错误')
