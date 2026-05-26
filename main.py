import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- WEB SUNUCUSU (7/24 AKTİF TUTMA) ---
app = Flask('')
@app.route('/')
def home(): return "Lien2 Bot 7/24 Aktif!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ID, LINK VE GÖRSEL AYARLARI ---
YETKILI_ROLLER = [1000462054488015042, 1000462280221266141, 1000462479832387615, 1000461367054188625, 1000461569139941507]
HOS_GELDIN_KANAL_ID = 1507136129751584828
TICKET_LOG_KANAL_ID = 1105043984088305664
TICKET_KATEGORI_ID = 1507136148479279267

GIF_URL = 'https://cdn.discordapp.com/attachments/1473662959250051165/1508894791604109343/acls.webp?ex=6a173348&is=6a15e1c8&hm=5e92574385ab5bbd03e3febd9edf3252dd9e7f5b9e2b4c054e9454e761b8c9ec&'
LOGO_URL = 'https://cdn.discordapp.com/attachments/1473662959250051165/1508894490427916438/L2_epic_discord.gif?ex=6a173300&is=6a15e180&hm=c50dd7a2f3020401b0abfc36fe481d97d8529ca78876358c26534c29cc9c778c&'
TICKET_AFIS_URL = 'https://media.discordapp.net/attachments/924941486322241606/1508894179345043497/logo_2.png?ex=6a1732b6&is=6a15e136&hm=a178601b1faf7054ab0b3cded51684a23e1ed1e743e09800abf24ad793d13be4&=&format=webp&quality=lossless&width=1575&height=864'

KRALLIK_ROLLER = {
    'bayrak_kirmizi': 1473752790458171568,
    'bayrak_sari': 1473752888546164897,
    'bayrak_mavi': 1473752930246070282
}
KARAKTER_ROLLER = {
    'rol_savasci': 1473750606161248480,
    'rol_ninja': 1473750645906341908,
    'rol_saman': 1473750696649297981,
    'rol_sura': 1473750745361944802
}

# --- KULLANICININ AÇIK BİLETİ VAR MI KONTROL ET ---
def kullanici_bileti_var(guild, user_id):
    kategori = guild.get_channel(TICKET_KATEGORI_ID)
    if kategori:
        for kanal in kategori.channels:
            if str(user_id) in [str(m.id) for m in kanal.overwrites]:
                return True
            # Kanal ismine göre de kontrol
            for perm_target, overwrite in kanal.overwrites.items():
                if isinstance(perm_target, discord.Member) and perm_target.id == user_id:
                    if overwrite.read_messages:
                        return True
    return False

# --- YARDIMCI FONKSİYONLAR ---
async def send_ticket_log(action, channel_name, opener, closer=None):
    log_channel = bot.get_channel(TICKET_LOG_KANAL_ID)
    if log_channel:
        color = 0x2ecc71 if action == "Açıldı" else 0xe74c3c
        embed = discord.Embed(title=f"🎫 Bilet {action}", color=color, timestamp=discord.utils.utcnow())
        embed.add_field(name="Kanal", value=f"`{channel_name}`", inline=True)
        embed.add_field(name="Bilet Sahibi", value=opener.mention, inline=True)
        if closer:
            embed.add_field(name="Kapatan Yetkili", value=closer.mention, inline=False)
        embed.set_footer(text="Lien2 Destek Log")
        embed.set_thumbnail(url=LOGO_URL)
        await log_channel.send(embed=embed)

async def kanal_kapat(i: discord.Interaction):
    await i.response.defer()
    messages = []
    async for msg in i.channel.history(limit=None, oldest_first=True):
        zaman = msg.created_at.strftime("%d/%m/%Y %H:%M")
        content = msg.content if msg.content else "[Görsel/Ek]"
        messages.append(f"[{zaman}] {msg.author.display_name}: {content}")

    chat_history = "\n".join(messages)
    file_name = f"log_{i.channel.name}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"Lien2 Bilet Kaydi\nKanal: {i.channel.name}\n" + "="*30 + "\n" + chat_history)

    log_channel = bot.get_channel(TICKET_LOG_KANAL_ID)
    if log_channel:
        with open(file_name, "rb") as f:
            df = discord.File(f, filename=file_name)
            embed_log = discord.Embed(title="🔒 Bilet Kapatıldı", color=0xe74c3c, timestamp=discord.utils.utcnow())
            embed_log.add_field(name="Kanal", value=f"`{i.channel.name}`", inline=True)
            embed_log.add_field(name="Kapatan", value=i.user.mention, inline=True)
            await log_channel.send(embed=embed_log, file=df)

    if os.path.exists(file_name): os.remove(file_name)
    await i.channel.delete()

# --- KAPAT BUTONU VIEW (PERSISTENT) ---
class KapatView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Kanalı Kapat", style=discord.ButtonStyle.danger, custom_id="kanal_kapat_btn")
    async def kapat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await kanal_kapat(interaction)

# --- BUTONLU LİNK GÖRÜNÜMÜ ---
class LinkButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label='Site', url='https://lien2.com.tr/index', style=discord.ButtonStyle.link, emoji="🔗"))
        self.add_item(discord.ui.Button(label='Tanıtım', url='https://tanitim.lien2.com.tr/', style=discord.ButtonStyle.link, emoji="📜"))
        self.add_item(discord.ui.Button(label='Kayıt Ol', url='https://lien2.com.tr/register', style=discord.ButtonStyle.link, emoji="📝"))
        self.add_item(discord.ui.Button(label='İndir', url='https://lien2.com.tr/download', style=discord.ButtonStyle.link, emoji="📥"))

# --- MODAL FORMLARI ---
class ApplicationModal(discord.ui.Modal):
    def __init__(self, title, app_type):
        super().__init__(title=title)
        self.app_type = app_type
        if app_type == "basvuru":
            self.q1 = discord.ui.TextInput(label="İsim ve Soy isminiz?", required=True)
            self.q2 = discord.ui.TextInput(label="Yaş ve Şehir?", required=True)
            self.q3 = discord.ui.TextInput(label="Müsaitlik Saatleriniz?", style=discord.TextStyle.paragraph, required=True)
            self.q4 = discord.ui.TextInput(label="Deneyimleriniz?", style=discord.TextStyle.paragraph, required=True)
            self.q5 = discord.ui.TextInput(label="Neden Biz?", style=discord.TextStyle.paragraph, required=True)
            for q in [self.q1, self.q2, self.q3, self.q4, self.q5]: self.add_item(q)
        else:
            self.p1 = discord.ui.TextInput(label="Platformunuz?", required=True)
            self.p2 = discord.ui.TextInput(label="Kanal Linkiniz?", required=True)
            self.p3 = discord.ui.TextInput(label="İçerik Günleriniz?", style=discord.TextStyle.paragraph, required=True)
            self.p4 = discord.ui.TextInput(label="Günlük Kaç Saat?", required=True)
            self.p5 = discord.ui.TextInput(label="Katkı Planınız?", style=discord.TextStyle.paragraph, required=True)
            for p in [self.p1, self.p2, self.p3, self.p4, self.p5]: self.add_item(p)

    async def on_submit(self, interaction: discord.Interaction):
        if kullanici_bileti_var(interaction.guild, interaction.user.id):
            return await interaction.response.send_message("⚠️ Mevcut bir biletin zaten açık!", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for r_id in YETKILI_ROLLER:
            role = interaction.guild.get_role(r_id)
            if role: overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = interaction.guild.get_channel(TICKET_KATEGORI_ID)
        channel = await interaction.guild.create_text_channel(name=f"{self.app_type}-{interaction.user.name}", overwrites=overwrites, category=category)
        await send_ticket_log("Açıldı", channel.name, interaction.user)

        embed = discord.Embed(title=f"💎 Yeni {self.app_type.capitalize()} Başvurusu", color=discord.Color.gold())
        embed.set_image(url=GIF_URL)
        embed.set_footer(text="Founder Lvs")
        for item in self.children: embed.add_field(name=item.label, value=item.value, inline=False)

        await channel.send(embed=embed, view=KapatView())
        await interaction.response.send_message(f"✅ Başvurunuz iletildi: {channel.mention}", ephemeral=True)

# --- SEÇİM VE TICKET GÖRÜNÜMLERİ ---
class SelectionView(discord.ui.View):
    def __init__(self, roles_dict, type_name):
        super().__init__(timeout=None)
        self.roles_dict = roles_dict
        self.type_name = type_name

    async def handle_selection(self, interaction, custom_id):
        role_id = self.roles_dict[custom_id]
        role = interaction.guild.get_role(role_id)
        if role in interaction.user.roles:
            return await interaction.response.send_message(f"⚠️ Zaten bu {self.type_name} seçimini yapmışsın!", ephemeral=True)
        for r_id in self.roles_dict.values():
            r = interaction.guild.get_role(r_id)
            if r and r in interaction.user.roles: await interaction.user.remove_roles(r)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"✅ {self.type_name} başarıyla güncellendi: {role.name}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    async def create_simple_ticket(self, interaction: discord.Interaction, label: str):
        if kullanici_bileti_var(interaction.guild, interaction.user.id):
            return await interaction.response.send_message("⚠️ Mevcut bir biletin zaten açık!", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for r_id in YETKILI_ROLLER:
            role = interaction.guild.get_role(r_id)
            if role: overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = interaction.guild.get_channel(TICKET_KATEGORI_ID)
        ch = await interaction.guild.create_text_channel(name=f"{label}-{interaction.user.name}", overwrites=overwrites, category=category)
        await send_ticket_log("Açıldı", ch.name, interaction.user)

        embed = discord.Embed(description=f"Selam {interaction.user.mention}, **{label}** kategorisinde bilet açtın.", color=0x2ecc71)
        embed.set_image(url=GIF_URL)
        embed.set_footer(text="Founder Lvs")

        await ch.send(embed=embed, view=KapatView())
        await interaction.response.send_message(f"✅ Kanal açıldı: {ch.mention}", ephemeral=True)

    @discord.ui.button(label="Destek", style=discord.ButtonStyle.danger, custom_id="ticket_destek")
    async def bug(self, interaction, button): await self.create_simple_ticket(interaction, "destek")
    @discord.ui.button(label="Küfür & Şikayet", style=discord.ButtonStyle.secondary, custom_id="ticket_sikayet")
    async def report(self, interaction, button): await self.create_simple_ticket(interaction, "sikayet")
    @discord.ui.button(label="Takım Başvurusu", style=discord.ButtonStyle.success, custom_id="ticket_basvuru")
    async def apply_team(self, interaction, button): await interaction.response.send_modal(ApplicationModal("Takım Başvurusu", "basvuru"))
    @discord.ui.button(label="Partnerlik", style=discord.ButtonStyle.primary, custom_id="ticket_partner")
    async def apply_partner(self, interaction, button): await interaction.response.send_modal(ApplicationModal("Partnerlik Başvurusu", "partner"))

# --- ETKINLIKLER ---
@bot.event
async def on_ready():
    print(f'🛡️ {bot.user.name} AKTIF!')
    bot.add_view(TicketView())
    bot.add_view(KapatView())
    await bot.change_presence(activity=discord.Game(name="Lien2"))
    keep_alive()

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(HOS_GELDIN_KANAL_ID)
    if channel:
        embed = discord.Embed(title='🛡️ Lien2 Krallığına Hoş Geldin!', description=f'Selam {member.mention}!', color=0xf1c40f)
        embed.set_image(url=GIF_URL); embed.set_footer(text="Founder Lvs")
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.command()
async def site(ctx):
    embed = discord.Embed(title=f"Merhaba {ctx.author.display_name}", description="**Site:** https://lien2.com.tr/index\n**Tanıtım:** https://tanitim.lien2.com.tr/\n**Kayıt:** https://lien2.com.tr/register\n**İndir:** https://lien2.com.tr/download", color=0xe74c3c)
    embed.set_thumbnail(url=LOGO_URL); embed.set_image(url=GIF_URL); embed.set_footer(text="Founder Lvs")
    await ctx.send(embed=embed, view=LinkButtons())

@bot.command()
@commands.has_permissions(administrator=True)
async def krallik_kur(ctx):
    view = SelectionView(KRALLIK_ROLLER, "Krallık")
    for key, label, style, emoji in [('bayrak_kirmizi', 'Shinsoo', discord.ButtonStyle.danger, '🔴'), ('bayrak_sari', 'Chunjo', discord.ButtonStyle.secondary, '🟡'), ('bayrak_mavi', 'Jinno', discord.ButtonStyle.primary, '🔵')]:
        btn = discord.ui.Button(label=label, style=style, custom_id=key, emoji=emoji); btn.callback = lambda i, k=key: view.handle_selection(i, k); view.add_item(btn)
    embed = discord.Embed(title="🚩 Lien2 Krallık Seçimi", description="Safını belirle!", color=0xffffff)
    embed.set_image(url=GIF_URL); embed.set_footer(text="Founder Lvs")
    await ctx.send(embed=embed, view=view)

@bot.command()
@commands.has_permissions(administrator=True)
async def rol_kur(ctx):
    view = SelectionView(KARAKTER_ROLLER, "Sınıf")
    for key, label, emoji in [('rol_savasci', 'Savaşçı', '🛡️'), ('rol_ninja', 'Ninja', '🏹'), ('rol_sura', 'Sura', '🔥'), ('rol_saman', 'Şaman', '✨')]:
        btn = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, custom_id=key, emoji=emoji); btn.callback = lambda i, k=key: view.handle_selection(i, k); view.add_item(btn)
    embed = discord.Embed(title="⚔️ Lien2 Karakter Sınıfı Seçimi", description="Yolunu seç!", color=0x2f3136)
    embed.set_image(url=GIF_URL); embed.set_footer(text="Founder Lvs")
    await ctx.send(embed=embed, view=view)

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket_kur(ctx):
    kurallar = (
        "**Sıra Bekleme:** Destek sürecinin yoğunluğuna göre\n"
        "değişiklik gösterebileceğini unutmayın. Lütfen\n"
        "sıranızın gelmesini sabırla bekleyin.\n\n"
        "**Doğru Kategori Seçimi:** Sorununuzla ilgili doğru\n"
        "kategoride ticket açmaya özen gösteriniz. Yanlış\n"
        "kategorilerde açılan talepler, çözüm sürecini\n"
        "uzatabilir.\n\n"
        "**Üslup ve Saygı:** Ticket oluştururken lütfen saygılı\n"
        "bir dil kullanın. Hakaret içeren, saldırgan veya\n"
        "saygısız ifadeler kabul edilmeyecektir.\n\n"
        "**Gerekli Bilgilerin Sağlanması:** Destek talebinizi\n"
        "açarken sorununuzla ilgili tüm gerekli bilgileri\n"
        "eksiksiz şekilde veriniz. Bu, çözüm sürecini\n"
        "hızlandıracaktır.\n\n"
        "**Sonuç Bilgilendirme:** Destek ekibi tarafından\n"
        "sorununuz çözüldüğünde, durumu geri bildirim\n"
        "sağlayarak destek ekibini bilgilendiriniz.\n\n"
        "**Çoklu Ticket Açmama:** Aynı konu için birden fazla\n"
        "ticket açmaktan kaçının. Bu, çözüm sürecini\n"
        "aksatabilir ve gereksiz yoğunluğa neden olabilir.\n\n"
        "**Ticket Güncellemesi:** Ticket'ınızla ilgili yeni bir\n"
        "gelişme olduğunda, yeni bir ticket açmak yerine\n"
        "mevcut ticket'ınızı güncelleyiniz.\n\n"
        "**Gereksiz Ticket Açmama:** Soruşturma\n"
        "gerektirmeyen ya da çözüm merkezindeki bilgilere\n"
        "ulaşabileceğiniz konular için ticket açmaktan\n"
        "kaçınınız.\n\n"
        "**Destek taleplerinizi açtığınızda, 10 dakika içinde\n"
        "geri dönüş yapılmadığı takdirde talepler\n"
        "otomatik olarak kapatılacaktır. Anlayışınız için\n"
        "teşekkür ederiz.**"
    )
    embed = discord.Embed(title="🎫 Lien2 Destek", description=f"İşlem seçiniz.\n\n{kurallar}", color=0x2ecc71)
    embed.set_image(url=TICKET_AFIS_URL); embed.set_footer(text="Founder Lvs")
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
@commands.has_permissions(manage_messages=True)
async def temizle(ctx, miktar: int): await ctx.channel.purge(limit=miktar + 1)

@bot.command()
@commands.has_permissions(administrator=True)
async def sosyal(ctx):
    embed = discord.Embed(title="🌐 Lien2 Resmi Bağlantılar", color=0x3498db)
    embed.add_field(name="📸 Instagram", value="[lienmt2](https://www.instagram.com/lienmt2/)", inline=False)
    embed.add_field(name="🌐 Web Site", value="[lien2.com.tr](https://lien2.com.tr/)", inline=False)
    embed.add_field(name="💬 Discord", value="https://discord.gg/lien2", inline=False)
    embed.add_field(name="▶️ YouTube", value="[@LienMt2](https://www.youtube.com/@LienMt2)", inline=False)
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=GIF_URL)
    embed.set_footer(text="Founder Lvs")
    await ctx.send(embed=embed)

bot.run(os.getenv('TOKEN'))
