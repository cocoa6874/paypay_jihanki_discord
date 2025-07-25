import discord
from discord.ext import commands
import os
from PayPaython_mobile import PayPay
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# セッションを保存。
bot.user_sessions = {}

# 自動ログイン用
token_path = "token.json"
if os.path.exists(token_path):
    try:
        with open(token_path, 'r') as f:
            tokens = json.load(f)

        for guild_id_str, access_token in tokens.items():
            try:
                guild_id = int(guild_id_str)
                paypay = PayPay(access_token=access_token)
                bot.user_sessions[guild_id] = paypay
                print(f"自動ログイン成功: サーバーID {guild_id}")
            except Exception as e:
                print(f"ログイン失敗（サーバー {guild_id_str}）: {e}")
    except Exception as e:
        print(f"token.json 読み込み失敗: {e}")
else:
    print("token.json が存在しません。自動ログインスキップ。")

@bot.event
async def on_ready():
    print(f'{bot.user}がログインしたよ')

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

if __name__ == "__main__":
    async def main():
        await load_cogs()
        await bot.start("ここにとーくん")
    asyncio.run(main())
