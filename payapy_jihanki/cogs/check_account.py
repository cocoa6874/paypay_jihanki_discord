import discord
from discord.ext import commands

class AccountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="check_account", description="PayPayアカウントの情報を表示します。")
    async def check_account(self, ctx):
        await ctx.defer()
        try:
            paypay = self.bot.user_sessions.get(ctx.guild.id)
            if not paypay:
                await ctx.followup.send("paypayログインしないと使えないよ(笑)")
                return

            profile = paypay.get_profile()
            await ctx.followup.send(f"""
ユーザー名 : {profile.name}
ユーザーID : {profile.external_user_id}
アイコン　 : {profile.icon}
""")
        except Exception as e:
            await ctx.followup.send(f"エラー発生 : {str(e)}")

def setup(bot):
    bot.add_cog(AccountCog(bot))
