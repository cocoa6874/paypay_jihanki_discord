import discord
from discord.ext import commands
import os
import json
from PayPaython_mobile import PayPay

class BuyPanelView(discord.ui.View):
    def __init__(self, bot, ctx, product_name, product_data):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.product_name = product_name
        self.product_data = product_data

        self.add_item(BuyButton(self))
        self.add_item(CheckStockButton(self))

class BuyButton(discord.ui.Button):
    def __init__(self, parent):
        super().__init__(label="購入する", style=discord.ButtonStyle.green)
        self.parent = parent

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PayLinkModal(self.parent))

class CheckStockButton(discord.ui.Button):
    def __init__(self, parent):
        super().__init__(label="値段・在庫確認", style=discord.ButtonStyle.gray)
        self.parent = parent

    async def callback(self, interaction: discord.Interaction):
        price = self.parent.product_data["price"]
        description = self.parent.product_data["description"]
        await interaction.response.send_message(f"価格: {price}\n在庫数: {len(description.splitlines())}", ephemeral=True)

class PayLinkModal(discord.ui.Modal):
    def __init__(self, parent):
        super().__init__(title="PayPayリンクを入力してください")
        self.parent = parent
        self.add_item(discord.ui.InputText(label="PayPayリンク", placeholder="https://pay.paypay.ne.jp/..."))

    async def callback(self, interaction: discord.Interaction):
        paypay_url = self.children[0].value.strip()

        try:
            guild_id = self.parent.ctx.guild.id
            paypay = self.parent.bot.user_sessions.get(guild_id)

            if not paypay:
                await interaction.response.send_message("paypayログインした？", ephemeral=True)
                return


            link_info = paypay.link_check(paypay_url)
            

            if not link_info or not hasattr(link_info, 'amount'):
                await interaction.response.send_message("PayPayリンクが無効です。", ephemeral=True)
                return

            expected_price = int(self.parent.product_data["price"])

            try:
                link_amount = int(link_info.amount)
                if link_amount != expected_price:
                    await interaction.response.send_message("金額が正しくないです。", ephemeral=True)
                    return
            except Exception as e:
                await interaction.response.send_message(f"金額チェックエラー: {str(e)}", ephemeral=True)
                return

            try:
                paypay.link_receive(paypay_url, link_info=link_info.raw)
            except Exception as e:
                await interaction.response.send_message(f"PayPay受け取りエラー: {str(e)}", ephemeral=True)
                return
            items = self.parent.product_data["description"].splitlines()

            if not items:
                await interaction.response.send_message("在庫がなし", ephemeral=True)
                return

            item = items.pop(0)
            self.parent.product_data["description"] = "\n".join(items)
            file_path = os.path.join("products", str(guild_id), f"{self.parent.product_name}.json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.parent.product_data, f, ensure_ascii=False, indent=2)

            embed = discord.Embed(title="購入完了", description=f"{self.parent.product_name}を購入しました。", color=discord.Color.blurple(),)
            embed.add_field(name="商品", value=f"{item}")
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("商品をDMに送信しました。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"エラーが発生しました: {str(e)}", ephemeral=True)

class SetBuyPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="set_buypanel", description="購入パネルを設置")
    async def set_buypanel(self, ctx):
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild.id)
        directory = os.path.join("products", guild_id)

        if not os.path.exists(directory):
            await ctx.followup.send("このサーバーにはまだ商品がありません。")
            return

        file_list = [f for f in os.listdir(directory) if f.endswith(".json")]
        if not file_list:
            await ctx.followup.send("このサーバーには商品がありません。")
            return

        view = ProductChoiceView(self.bot, ctx, file_list, directory)
        await ctx.followup.send("設置する商品を選んでください。", view=view)

class ProductChoiceView(discord.ui.View):
    def __init__(self, bot, ctx, file_list, directory):
        super().__init__(timeout=60)
        self.add_item(ProductChoiceSelect(bot, ctx, file_list, directory))

class ProductChoiceSelect(discord.ui.Select):
    def __init__(self, bot, ctx, file_list, directory):
        options = [discord.SelectOption(label=file[:-5], value=file) for file in file_list]
        super().__init__(placeholder="商品を選択", options=options)
        self.bot = bot
        self.ctx = ctx
        self.directory = directory

    async def callback(self, interaction: discord.Interaction):
        file_name = self.values[0]
        product_name = file_name[:-5]
        file_path = os.path.join(self.directory, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            product_data = json.load(f)

        embed = discord.Embed(title=product_name, description="商品はDMに送信されます。")
        view = BuyPanelView(self.bot, self.ctx, product_name, product_data)
        await interaction.response.send_message(embed=embed, view=view)

def setup(bot):
    bot.add_cog(SetBuyPanelCog(bot))
