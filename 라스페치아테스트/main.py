import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
IMAGE_DIR = 'images'

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} 연결되었습니다.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image'):
                file_path = os.path.join(IMAGE_DIR, attachment.filename)
                await attachment.save(file_path)
                await message.channel.send(f'{attachment.filename} 이미지가 저장되었습니다.')

    if message.content.lower() == '팔목록':
        image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.avif','.webp'))]
        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(IMAGE_DIR, x)), reverse=True)

        await send_image_list(message.channel, image_files)

async def send_image_list(channel, image_files):
    embed = discord.Embed(title="이미지 파일 목록")
    view = ImageListView(image_files)

    for i, file in enumerate(image_files):
        embed.add_field(name=f"이미지 {i + 1}", value=file, inline=False)

    await channel.send(embed=embed, view=view)

class ImageListView(discord.ui.View):
    def __init__(self, image_files):
        super().__init__()
        self.image_files = image_files
        self.add_buttons()

    def add_buttons(self):
        for i in range(len(self.image_files)):
            button = discord.ui.Button(label=str(i + 1), style=discord.ButtonStyle.primary)
            async def callback(interaction, index=i):
                await interaction.response.defer() # 응답 지연시간 추가. 안그러면 렉걸린다.
                await send_image(interaction.message.channel, self.image_files, index)
            button.callback = callback
            self.add_item(button)

        if len(self.image_files) > 5:
            next_button = discord.ui.Button(label="다음", style=discord.ButtonStyle.primary)
            async def next_callback(interaction):
                await interaction.response.defer() # 응답 지연 추가(쿨다운용)
                await send_image_list(interaction.message.channel, self.image_files[5:])
            next_button.callback = next_callback
            self.add_item(next_button)

async def send_image(channel, image_files, index):
    if 0 <= index < len(image_files):
        file_path = os.path.join(IMAGE_DIR, image_files[index])
        embed = discord.Embed(title=f"이미지 {index + 1}")
        embed.set_image(url=f"attachment://{image_files[index]}")
        file = discord.File(file_path)
        await channel.send(file=file, embed=embed)
    else:
        await channel.send("해당 이미지를 찾을 수 없습니다.")

client.run(TOKEN)