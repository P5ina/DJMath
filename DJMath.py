﻿import discord
import youtube_dl
import subprocess
import urllib
from bs4 import BeautifulSoup
from discord.ext import commands

TOKEN ='NDk4MTYzMzQyMDc5NDI2NTcw.DppuaA.uSJG9JYJXhlTHDpgEuKTsCEHja8'

bot = commands.Bot(command_prefix='!')
players = {}
queues = {}


def check_queue(id):
    print('Checking queue with id: {}'.format(id))
    if queues[id] != []:
        print('Is not empty.')
        player = queues[id].pop(0)
        print(player.title)
        players[id] = player
        player.start()
        channel = bot.get_channel('498499824316973077')
        

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
    player = await voice_client.create_ytdl_player(search(search_text), after=lambda: check_queue(server.id))
    if player.duration < 301:
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