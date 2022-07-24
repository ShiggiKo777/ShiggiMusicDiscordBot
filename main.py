from asyncio.windows_events import NULL
import discord
import asyncio
import os
import nacl
import csv
from discord.ext import commands
from discord.voice_client import VoiceClient
from random import shuffle

#Настройки
RootMusicFolder = "DISK:/SomeFolder/" #укажи путь к месту где находятся папки с музыкой (каждая папка - это плейлист)
DefaultPlaylistName = "SomeSubfolder" #укажи папку с музыкой, которая будет играть по умолчанию (если неверно задан код плейлиста)
FFmpegPath = "DISK:/PathToFFmpeg" #путь до библиотеки FFmpeg (указать путь до ffmpeg.exe)
BotToken = 'token' #токен вашего бота
########

bot = commands.Bot(command_prefix = '!')
songs = []

folders = {}
SongId = -1
PlaylistId = 0
ArraySize = 0

bStopPlaying = False

global ctx_global

VoiceClientRef = NULL

event = asyncio.Event()

@bot.event
async def on_ready():
    print('------')
    print(f'Logged in as {bot.user.name} {bot.user.id}')
    print('------')

@bot.command(pass_context=True)
async def start(ctx):
    with open(RootMusicFolder + "playlist.csv", mode='r') as infile:
        reader = csv.reader(infile)
        global folders
        folders = {rows[0]:rows[1] for rows in reader}
        print(folders)
    author = ctx.message.author
    channel = author.voice.channel
    await channel.connect()
    await ctx.send('rock on!')

@bot.command(pass_context=True)
async def end(ctx):
    server = ctx.message.guild.voice_client
    await server.disconnect()
    await ctx.send('rock off...')

@bot.command(pass_context=True)
async def p(ctx, playlist="pe"):
    global bStopPlaying
    global VoiceClientRef
    
    if VoiceClientRef:
        if VoiceClientRef.is_playing():
            bStopPlaying = True
            await stop_music(ctx)
    else:
        server = ctx.message.guild
        VoiceClientRef = server.voice_client       

    global PlaylistId
    PlaylistId = playlist

    global ctx_global
    ctx_global = ctx

    bStopPlaying = False
    
    await ctx.send('start playing')
    
    player.prepare_plaing()
  
@bot.command(pass_context=True)
async def next(ctx):
    if VoiceClientRef:
        if VoiceClientRef.is_playing():
            VoiceClientRef.stop()

@bot.command(pass_context=True)
async def stop(ctx):   
    await stop_music(ctx)

async def stop_music(ctx):  
        global bStopPlaying
        bStopPlaying = True

        if VoiceClientRef:
            if VoiceClientRef.is_playing():     
                VoiceClientRef.stop() 

        await ctx.send('all stops')

class player:
    def prepare_plaing():
        songs.clear()
        PlaylistFolder = RootMusicFolder + player.get_folder(PlaylistId)
        print (PlaylistFolder)
        for root, dirs, files in os.walk(PlaylistFolder):
            for file in files:
                if file.endswith(".mp3"):
                     songs.append(os.path.join(root, file))
    
        global ArraySize
        ArraySize = len(songs)

        if (ArraySize <= 0):
            return

        global SongId
        SongId = -1

        shuffle(songs)
        #print(f'prepare music, size {ArraySize}')
        player.play_next()

    def play_next():
        global bStopPlaying

        if bStopPlaying:
            print(f'command stop music')
            return

        global SongId
        SongId = SongId + 1
        
        if ArraySize - 1 >= SongId and SongId >= 0:
            dirname = os.path.dirname(__file__)
            ffmpeg_path = os.path.join(dirname, FFmpegPath)

            filename = songs[SongId]

            #sourse_pcm = (discord.FFmpegPCMAudio(executable=ffmpeg_path, source=filename))
            sourse_pcm = discord.FFmpegOpusAudio(source=filename, executable=ffmpeg_path, bitrate=192)
            print(f'now playing {filename} id {SongId} max {ArraySize - 1}')
            VoiceClientRef.play((sourse_pcm), after=lambda e: player.play_next())
        else:
            print(f'playlist finished')
            player.prepare_plaing()
    
    def get_folder(playlist_id):    
        if playlist_id in folders:       
            return folders[playlist_id]
        else:
            return DefaultPlaylistName
     
bot.run(BotToken)