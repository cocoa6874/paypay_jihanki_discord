import discord
from discord.ext import commands

class ClaimLinkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command(name="claim_link", description="指定した金額のpaypay請求リンクを作ります。")
    async def claim_link(self, ctx, amount: float):
        await ctx.defer()
        
        paypay = self.bot.user_sessions.get(ctx.guild.id)
        if not paypay:
            await ctx.followup.send("paypayログインしないと使えないよ(笑)")
            return
        
        create_link = paypay.create_p2pcode(amount)
        
        try:
            await ctx.followup.send(f"請求リンク: {create_link.p2pcode}")
        except Exception as e:
            await ctx.followup.send(f"エラー発生 : {str(e)}")


def setup(bot):
    bot.add_cog(ClaimLinkCog(bot))