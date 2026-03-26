import os
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # необязательно, но для быстрых команд лучше указать

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Укажи свои файлы здесь
songs = {
    "Сумна пісня від сумного хлопчика с псоріазом": "1.mp3",
}

class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="join", description="Подключить бота к твоему голосовому каналу")
    async def join(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Эта команда только на сервере.", ephemeral=True)
            return

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("Сначала зайди в голосовой канал.", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc is None:
            await channel.connect()
            await interaction.response.send_message(f"Подключился к {channel.name}")
        else:
            await vc.move_to(channel)
            await interaction.response.send_message(f"Перешёл в {channel.name}")

    @app_commands.command(name="leave", description="Отключить бота от голосового канала")
    async def leave(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Эта команда только на сервере.", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if vc is None:
            await interaction.response.send_message("Я не в голосовом канале.", ephemeral=True)
            return

        await vc.disconnect()
        await interaction.response.send_message("Отключился.")

    @app_commands.command(name="list", description="Показать список доступных песен")
    async def list_songs(self, interaction: discord.Interaction):
        names = "\n".join(f"- {name}" for name in songs.keys())
        await interaction.response.send_message(f"Доступные песни:\n{names}")

    @app_commands.command(name="stop", description="Остановить музыку")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Эта команда только на сервере.", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("Остановил музыку.")
        else:
            await interaction.response.send_message("Сейчас ничего не играет.", ephemeral=True)

    @app_commands.command(name="play", description="Включить песню")
    @app_commands.describe(name="Название песни из /list")
    async def play(self, interaction: discord.Interaction, name: str):
        if not interaction.guild:
            await interaction.response.send_message("Эта команда только на сервере.", ephemeral=True)
            return

        if name not in songs:
            await interaction.response.send_message(
                f"Песня не найдена. Доступные: {', '.join(songs.keys())}",
                ephemeral=True
            )
            return

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("Сначала зайди в голосовой канал.", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc is None:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        if vc.is_playing():
            vc.stop()

        source = discord.FFmpegPCMAudio(songs[name], executable="ffmpeg")
        vc.play(source)

        await interaction.response.send_message(f"Сейчас играет: {name}")

async def setup_bot():
    await bot.add_cog(MusicCog(bot))

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    try:
        # Регистрируем команды
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Guild sync OK: {len(synced)} команд")
        else:
            synced = await bot.tree.sync()
            print(f"Global sync OK: {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка sync: {e}")

async def main():
    if not TOKEN:
        raise RuntimeError("Не задан DISCORD_TOKEN")

    await setup_bot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
