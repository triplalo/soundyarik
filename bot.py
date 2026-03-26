import os
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

songs = {
    "Сумна пісня від сумного хлопчика с псоріазом": "music/1.mp3",
    "track2": "music/track2.mp3",
    "track3": "music/track3.mp3",
}

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="Подключить бота к голосовому каналу")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.response.send_message("Сначала зайди в голосовой канал.", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            await channel.connect()
            await interaction.response.send_message(f"Подключился к {channel}")
        else:
            await voice_client.move_to(channel)
            await interaction.response.send_message(f"Перешёл в {channel}")

    @app_commands.command(name="leave", description="Отключить бота от голосового канала")
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            await interaction.response.send_message("Я не в голосовом канале.", ephemeral=True)
            return

        await voice_client.disconnect()
        await interaction.response.send_message("Отключился.")

    @app_commands.command(name="list", description="Список песен")
    async def list_songs(self, interaction: discord.Interaction):
        song_list = "\n".join([f"- {name}" for name in songs.keys()])
        await interaction.response.send_message(f"Доступные песни:\n{song_list}")

    @app_commands.command(name="stop", description="Остановить музыку")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("Музыка остановлена.")
        else:
            await interaction.response.send_message("Сейчас ничего не играет.", ephemeral=True)

    @app_commands.command(name="play", description="Включить песню")
    @app_commands.describe(name="Название песни")
    async def play(self, interaction: discord.Interaction, name: str):
        if name not in songs:
            await interaction.response.send_message(
                f"Песня не найдена. Доступные: {', '.join(songs.keys())}",
                ephemeral=True
            )
            return

        if interaction.user.voice is None:
            await interaction.response.send_message("Сначала зайди в голосовой канал.", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(songs[name], executable=FFMPEG_PATH)
        voice_client.play(source)

        await interaction.response.send_message(f"Сейчас играет: {name}")

@bot.event
async def on_ready():
    await bot.add_cog(MusicBot(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")

    print(f"Бот запущен как {bot.user}")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN не найден в переменных окружения")

bot.run(TOKEN)
