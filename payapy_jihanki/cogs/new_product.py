import discord
from discord.ext import commands
import os
import json

class ProductCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="new_product", description="新しい商品を追加します")
    async def new_product(self, ctx, product_name: str):
        await ctx.defer()

        guild_id = str(ctx.guild.id)
        directory = os.path.join("products", guild_id)
        file_path = os.path.join(directory, f"{product_name}.json")

        if not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(file_path):
            await ctx.followup.send(f"商品`{product_name}`はすでに存在しています。")
            return

        # 中身は価格と商品内容の空テンプレ
        product_data = {
            "price": "",
            "description": ""
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(product_data, f, ensure_ascii=False, indent=2)
            await ctx.followup.send(f"商品{product_name}を作成しました。")
        except Exception as e:
            await ctx.followup.send(f"エラーが発生しました: {str(e)}")

def setup(bot):
    bot.add_cog(ProductCog(bot))
