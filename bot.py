import miraicle
import json
from plugins import *

qq = 2752038425
verify_key = 'd92n3duch23h'
port = 8081

bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
bot.set_filter(miraicle.GroupSwitchFilter(r"config/group_switch.json"))
bot.run()
