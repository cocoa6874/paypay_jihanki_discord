import discord
from discord.ext import commands
import os
import json

class EditProductView(discord.ui.View):
    def __init__(self, bot, ctx, file_list, directory):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx
        self.directory = directory
        self.add_item(ProductSelect(self, file_list))

class ProductSelect(discord.ui.Select):
    def __init__(self, parent_view, file_list):
        options = [
            discord.SelectOption(label=file[:-5], value=file)
            for file in file_list if file.endswith(".json")
        ]
        super().__init__(placeholder="編集する商品を選んでくさい", min_values=1, max_values=1, options=options)
        self._parent_view = parent_view
        
    async def callback(self, interaction: discord.Interaction):
        file_name = self.values[0]
        file_path = os.path.join(self._parent_view.directory, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        await interaction.response.send_modal(EditProductModal(file_path, existing_data))



class EditProductModal(discord.ui.Modal):
    def __init__(self, file_path, existing_data):
        super().__init__(title="商品を編集")
        self.file_path = file_path

        price = existing_data.get("price", "")
        description = existing_data.get("description", "")

        self.add_item(discord.ui.InputText(label="価格", style=discord.InputTextStyle.short, value=price))
        self.add_item(discord.ui.InputText(label="商品内容 １行に一個商品を入力", style=discord.InputTextStyle.paragraph, value=description))


    async def callback(self, interaction: discord.Interaction):
        try:
            price = self.children[0].value
            description = self.children[1].value.strip()

            data = {
                "price": price,
                "description": description
            }

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            await interaction.response.send_message("商品を更新しました。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"エラーが発生しました: {str(e)}", ephemeral=True)


class EditProductCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="edit_product", description="商品を編集します")
    async def edit_product(self, ctx):
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild.id)
        directory = os.path.join("products", guild_id)

        if not os.path.exists(directory):
            await ctx.followup.send("このサーバーにはまだ商品がありません。")
            return

        file_list = os.listdir(directory)
        if not file_list:
            await ctx.followup.send("このサーバーには商品がありません。")
            return

        view = EditProductView(self.bot, ctx, file_list, directory)
        await ctx.followup.send("編集する商品を選んでください。", view=view)

def setup(bot):
    bot.add_cog(EditProductCog(bot))
