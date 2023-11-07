# Surise Bot

***A Mirai Bot based on Miraicle, born for OI.***

基于 Miraicle 的 Mirai QQ 机器人，为 OI 而生。

## 指令用法

### OI Extend 模块
1. /duel bind <洛谷UID>：绑定洛谷账号
2. /duel list：查看当前正在进行的对战
3. /duel rank：查看 Duel Rating 排行榜
4. /duel problem <Rating>：随机跳题
5. /duel begin @user <Rating>：发起 Duel
6. /duel accpet：接受 Duel
7. /duel reject：拒绝 Duel
8. /duel judge：完成 Duel 并结算
9. /duel change：发起换题请求
10. /duel giveup：投降
11. /duel cancel：主动取消
12. /today @user：今日做题情况
13. /today report：所有人今日做题排行

### Essentials 模块
1. /hello：检查 Bot 存活性
2. /admin list：查看管理员列表
3. /admin add @user：添加管理员
4. /admin remove @user：移除管理员
5. /test：检查网络连接，防止洛谷日爆
6. /about：版本信息

### GPT-Plug 模块
输入 “> ” + 问题（尖括号右侧有一个空格）向 ChatGPT 提问\
API 服务由 [Gestar Cloud](https://www.gestar.cloud/) 提供

## 部署

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

打开 bot.py，修改以下内容：

```python
qq = 2752038425 # 机器人 QQ 号
verify_key = 'd92n3duch23h' # mirai-api-http 密钥
port = 8081 # # mirai-api-http 的 HTTP 服务端口
```

### 3. 运行

```bash
python bot.py
```

### 4. 在群中启用功能

在群众发送 `/switcher enable all` 启用全部模块，或使用 `/switcher enable <Module>` 启用特定模块。