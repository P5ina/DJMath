import discord
import youtube_dl
import subprocess
import urllib
import os
import asyncio
from bs4 import BeautifulSoup
from discord.ext import commands

from discord import opus

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',

             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']





def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True
    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

    raise RuntimeError('Could not load an opus lib. Tried %s' %
                       (', '.join(opus_libs)))
load_opus_lib()

TOKEN ='NDk4MTYzMzQyMDc5NDI2NTcw.DppuaA.uSJG9JYJXhlTHDpgEuKTsCEHja8'

bot = commands.Bot(command_prefix='!')
players = {}
queues = {}


def check_queue(server):
    id = server.id
    print('Checking queue with id: {}'.format(id))
    if id in queues and queues[id] != []:
        print('Is not empty.')
        player = queues[id].pop(0)
        print(player.title)
        players[id] = player
        player.start()
        
    else:
        from discord.compat import run_coroutine_threadsafe
        channel = bot.get_channel('498141280199507969')
        print('Retrying...')
        coro = replay_song(server)
        fut = run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            print('error')
            pass        

async def replay_song(server):
    voice_client = bot.voice_client_in(server)
    player = await voice_client.create_ytdl_player(players[server.id].url, after=lambda: check_queue(server))
    players[server.id] = player
    player.start()

@bot.event
async def on_ready():
    print('DJ bot is online')
    radio_channel = bot.get_channel('498135784503902218')
    await bot.join_voice_channel(radio_channel)
    channel = bot.get_channel('498499824316973077')
    #await bot.send_message(channel,'Бот обновлен:\n1.Подгрузка видео быстрее\n2.Выводится длина видео')
    print('Bot joined to channel')  
    

@bot.command(pass_context = True)
@commands.has_role('Тестер ботов')
async def join(ctx):
    await bot.join_voice_channel(bot.get_channel('498135784503902218'))
    print ('Joining to channel: {}'.format(bot.get_channel('498135784503902218')))

@bot.command(pass_context = True)
@commands.has_role('Тестер ботов')
async def leave(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    await voice_client.disconnect()
    print('DJ is leaving')

@bot.command(pass_context = True)
async def play(ctx):
    search_text = ctx.message.content[6:]
    print ('\n{}\n'.format(search_text))
    print ('Channel id: {}'.format(ctx.message.channel.id))
    server = ctx.message.server
    channel = ctx.message.channel
    voice_client = bot.voice_client_in(server)
    player = await voice_client.create_ytdl_player(search(search_text), after=lambda: check_queue(server))
    if player.duration < 361:
        if server.id in queues and queues[server.id] != []:
            queues[server.id].append(player)
            await bot.send_message(channel,'Добавлено в очередь: `{}`. Благодарим за терпение.'.format(player.title))
        elif server.id in players and not players[server.id].is_done():
            print(players[server.id].is_done())
            queues[server.id] = [player]
            await bot.send_message(channel,'Добавлено в очередь: `{}`. Благодарим за терпение.'.format(player.title))
        else:
            players[server.id] = player
            await bot.send_message(channel,'Сейчас играет: `{}`. Наслаждайтесь!'.format(player.title))
            player.start()
    else:
        await bot.send_message(channel,'Видео: `{}`, слишком длинное: {}:{}!'.format(player.title, player.duration / 60, player.duration % 60))


@bot.command(pass_context = True)
@commands.has_role('Тестер ботов')
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()
    
@bot.command(pass_context = True)
@commands.has_role('Тестер ботов')
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

@bot.command(pass_context = True)    
async def skip(ctx):
    author = ctx.message.author
    server = ctx.message.server
    channel_bot = bot.get_channel('505846043733262338')
    await bot.send_message(channel_bot, 'b.level '+ author.mention)
    msg = await bot.wait_for_message(author=server.get_member('496328098325725214'),channel=channel_bot)
    if int(msg.content) >= 10:
        id = ctx.message.server.id
        players[id].stop()
    

@bot.command(pass_context = True)
async def queue(ctx):
    id = ctx.message.server.id
    channel = ctx.message.channel
    if id in players and id in queues:
        outstr = 'Сейчас играет: {}\nОчередь:\n'.format(players[id].title)
        for i in range(len(queues[id])):
            outstr += '{}: {}\n'.format(i+1, queues[id][i].title)
    else:
        outstr = 'Ничего нет'
    await bot.send_message(channel, outstr)
def search(text):
    query = urllib.parse.quote(text)
    print('Make query: {}'.format(query))
    url = "https://www.youtube.com/results?search_query=" + query
    print('Finding in this url: {}'.format(url))
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    result = 'https://www.youtube.com' + soup.findAll(attrs={'class':'yt-uix-tile-link'})[0]['href']
    print('Finded: {}'.format(result))
    return result

bot.run(TOKEN)