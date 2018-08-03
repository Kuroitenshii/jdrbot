import discord
from discord.ext import commands
import asyncio
import youtube_dl

bot = commands.Bot(command_prefix='')

@bot.event
async def on_message(message):
    if str(message.author) != "JdrBot#8016":
        channel = message.channel
        author = str(message.author)
        if 'bite' in message.content:
            await channel.send("Oh, une bite, j'aime ça")
        await bot.process_commands(message)

@bot.command()
async def Salut(ctx):
    author = str(ctx.author.display_name)
    await ctx.send("Salut "+author)

@bot.command()
async def Ça(ctx, arg):
    author = str(ctx.author.display_name)
    if arg == "va?":
        await ctx.send("Oui "+author+" et toi ?")

@bot.command()
async def JugementDernier(ctx):
    await ctx.send("J'invoque les âmes des sept Répurgateurs d'Astreciel !")
    await asyncio.sleep(2)
    await ctx.send("Laissez mon bras servir votre cause éternelle !")
    await asyncio.sleep(2)
    await ctx.send("Que le jugement dernier rende son verdict !")

@bot.command()
async def Apocalypse(ctx):
    await ctx.send("Puissent les âmes d'outre-tombe quitter les affres de l'oubli !")
    await asyncio.sleep(2)
    await ctx.send("Confiez-moi l'héritage de vos connaissances infinies !")
    await asyncio.sleep(2)
    await ctx.send("Que l'apocalypse sonne le glas des vivants !")

@bot.command()
async def Cataclysme(ctx):
    await ctx.send("Je fais appel à la puissance des éthers !")
    await asyncio.sleep(2)
    await ctx.send("Soyez le bras armé de ma colère !")
    await asyncio.sleep(2)
    await ctx.send("Que le cataclysme se déchaîne !")

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')

bot.add_cog(Music(bot))

bot.run('NDc0Njk5MzAxMjg1NjU4NjM1.DkUS7g.-EMo9lU8dfdVi_oStJf212TBv1U')
