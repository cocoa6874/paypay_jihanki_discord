import discord
from discord.ext import commands
from PayPaython_mobile import PayPay
import json
import os

class LoginCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_sessions = {}

    @discord.slash_command(name="login_paypay", description="PayPayにログインします")
    async def paypay_login(self, ctx, phone: str, password: str):
        await ctx.defer()
        try:
            paypay = PayPay(phone=phone, password=password)
            self.user_sessions[ctx.author.id] = paypay
            await ctx.followup.send("届いたURLをこのチャットに送信してください。開いてはいけません！絶対に開かずに送信してね")
        except Exception as e:
            await ctx.followup.send(f"ログインエラー: {str(e)}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        paypay = self.user_sessions.get(message.author.id)
        if paypay:
            url_or_id = message.content.strip()
            try:
                paypay.login(url_or_id)

                # paypay tokenを保存
                token_path = "token.json"
                if os.path.exists(token_path) and os.path.getsize(token_path) > 0:
                    with open(token_path, 'r') as f:
                        tokens = json.load(f)
                else:
                    tokens = {}

                tokens[str(message.guild.id)] = paypay.access_token

                with open(token_path, 'w') as f:
                    json.dump(tokens, f, indent=2)

                self.bot.user_sessions[message.guild.id] = paypay
                await message.channel.send("PayPayログイン成功！")

                # 一時セッションを削除。
                del self.user_sessions[message.author.id]

            except Exception as e:
                await message.channel.send(f"ログインエラー: {str(e)}")

def setup(bot):
    bot.add_cog(LoginCog(bot))