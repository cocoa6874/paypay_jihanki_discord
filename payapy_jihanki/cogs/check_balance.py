import discord
from discord.ext import commands

class BalanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="check_balance", description="現在のPayPay残高を確認します")
    async def check_balance(self, ctx):
        await ctx.defer()
        paypay = self.bot.user_sessions.get(ctx.guild.id)
        if not paypay:
            await ctx.followup.send("paypayログインしないと使えないよ(笑)")
            return

        balance = paypay.get_balance()
                
        embed = discord.Embed(title="paypay残高", color=discord.Color.blurple(),)
        embed.add_field(name="**総残高**", value=f"{balance.all_balance}円", inline=False)
        embed.add_field(name="**使用可能残高**", value=f"{balance.useable_balance}円", inline=False)
        embed.add_field(name="**マネラ**", value=f"{balance.money_light}円", inline=False)
        embed.add_field(name="**マネー**", value=f"{balance.money}円", inline=False)
        embed.add_field(name="**ポイント**", value=f"{balance.points}円", inline=False)
        await ctx.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(BalanceCog(bot))
