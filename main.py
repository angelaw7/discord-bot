import discord
import os
import requests
import json
import random

from league import *
import twitch
from udpy import UrbanClient

from discord.ext.commands import Bot

from dotenv import load_dotenv
load_dotenv()

bot = Bot(command_prefix='==')
udef = UrbanClient()


@bot.event
async def on_ready():
    await bot.change_presence(
      status=discord.Status.online,
      activity=discord.Game("Prefix: ==")
      )
    print('Ready')


@bot.event
async def on_message(message):

    await bot.process_commands(message)
    if message.author == bot.user:
        return


# Add reaction to add role
@bot.event
async def on_raw_reaction_add(payload):

    if payload.member.bot:
        pass

    else:
        with open('react_role.json') as react_file:
            data = json.load(react_file)

        for x in data:
            if x['emoji'] == payload.emoji.name and x['message_id'] == payload.message_id:
                role = discord.utils.get(bot.get_guild(payload.guild_id).roles, id=x['role_id'])

                await payload.member.add_roles(role)


# Remove reaction to remove role
@bot.event
async def on_raw_reaction_remove(payload):

    with open('reactrole.json') as react_file:
        data = json.load(react_file)

        for x in data:
            if x['emoji'] == payload.emoji.name and x['message_id'] == payload.message_id:
                role = discord.utils.get(bot.get_guild(payload.guild_id).roles, id=x['role_id'])

                await bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)


# Create react for role message
@bot.command()
async def reactrole(ctx, emoji, role: discord.Role, *, message):
    if ctx.author.id == os.getenv('REACTION_USER_ID') and ctx.channel.id == os.getenv('REACTION_CHANNEL_ID'):
        emb = discord.Embed(description=message)
        msg = await ctx.channel.send(embed=emb)
        await msg.add_reaction(emoji)

        with open('reactrole.json') as json_file:
            data = json.load(json_file)

            new_react_role = {
                'role_name': role.name,
                'role_id': role.id,
                'emoji': emoji,
                'message_id': msg.id
            }

            data.append(new_react_role)

        with open('reactrole.json', 'w') as j:
            json.dump(data, j, indent=4)


# Searches basic information about an anime
@bot.command()
async def sa(ctx, *args):
    q = "+".join(args)
    URL = "https://api.jikan.moe/v3/search/anime?q=" + q
    response = requests.get(URL)
    first_res = response.json()['results'][0]
    mal_id = first_res['mal_id']

    URL_DETAILS = "https://api.jikan.moe/v3/anime/" + str(mal_id)
    response_details = requests.get(URL_DETAILS).json()
    full_desc = response_details['synopsis']

    anime_description = (full_desc[:1010] + '...') if len(full_desc) > 1010 else full_desc

    embed = discord.Embed(title=first_res['title'], color=0x9b6dbe, url=response_details['url'])

    embed.add_field(name="Synopsis", value=anime_description, inline=False)
    embed.add_field(name="Rating", value=str(response_details['score']) + " (" + str(response_details['scored_by']) + ")", inline=True)
    embed.add_field(name="Episodes", value=response_details['episodes'], inline=True)
    embed.add_field(name="Premiered" if response_details['premiered'] else "Released", value=response_details['premiered'] if response_details['premiered'] else response_details['aired']['string'], inline=True)

    embed.set_thumbnail(
              url=first_res['image_url'])

    await ctx.channel.send(embed=embed)


# Searches a player's ranked stats and top played champions in League
@bot.command()
async def sr(ctx, summoner_name, help="Enter summoner name"):
    summoner_ID_json = request_summoner_data(summoner_name, API_key)

    ID = str(summoner_ID_json["id"])
    ranked_data_json = request_ranked_data(ID, API_key)

    summoner_name_formatted = ranked_data_json[0]["summonerName"]

    def format_ranked_data(type):
        queue_type = ranked_data_json[type]["queueType"]
        tier = ranked_data_json[type]["tier"]
        division = ranked_data_json[type]["rank"]
        lp = ranked_data_json[type]["leaguePoints"]
        qtype_wr = (ranked_data_json[type]["wins"]) / (
            ranked_data_json[type]["wins"] +
            ranked_data_json[type]["losses"]) * 100
        return [queue_type, tier, division, lp, qtype_wr]

    # Ranked data
    try:
        ranked_data = []
        for i in range(len(ranked_data_json)):
            ranked_data.append(list(format_ranked_data(i)))
    except:
        None

    # Top 3 most played champs
    mastery_points_json = request_top_champs(ID, API_key)
    top_champs = {}
    for i in range(3):
        champ_ID = mastery_points_json[i]["championId"]
        champ_points = mastery_points_json[i]["championPoints"]
        champ_level = mastery_points_json[i]["championLevel"]
        top_champs[champ_ID] = [champ_points, champ_level]

    try:
        embedRank = discord.Embed(title=summoner_name_formatted,
                                  color=0x9b6dbe)
        embedRank.set_thumbnail(
            url="https://static.wikia.nocookie.net/leagueoflegends/images/7/76/LoL_Icon.png"
        )
        try:
            for i in range(len(ranked_data)):
                embedRank.add_field(name=ranked_data[i][0],
                                    value=(ranked_data[i][1]).capitalize() +
                                    " " + ranked_data[i][2] + ", " +
                                    str(ranked_data[i][3]) + " lp (" +
                                    str(round(ranked_data[i][4])) + "%wr)",
                                    inline=False)
        except:
            None

        for k in top_champs.keys():
            new_k = id_to_champ(str(k))
            embedRank.add_field(name=new_k,
                                value=str(top_champs[k][0]) +
                                " mastery points (M" + str(top_champs[k][1]) +
                                ")",
                                inline=True)

        await ctx.channel.send(embed=embedRank)

    except:
        await ctx.channel.send("No rank")


# Purges a number of messages
@bot.command(name='purge', pass_context=True)
async def purge(ctx, num):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=int(num) + 1)
    else:
        await ctx.channel.send("Command restricted to admin")


# Coin Flip
@bot.command()
async def cf(ctx):
    flip = random.randint(0, 1)
    if flip == 0:
        await ctx.channel.send("heads")
    else:
        await ctx.channel.send("tails")


# Searches a word on Urban Dictionary
@bot.command()
async def ud(ctx, word, help="Search a word through Urban Dictionary"):
    define = udef.get_definition(str(word))
    definitions = ""

    for definition in define:
        formatted = ""
        for letter in str(definition):
            if letter not in ["[", "]"]:
                formatted += letter
        definitions += "\n" + (formatted)
    embedDef = discord.Embed(title=word,
                             description=definitions,
                             color=0x9b6dbe)
    await ctx.channel.send(embed=embedDef)


@bot.command()
async def stream(ctx, streamer):
    twitch.main(streamer)


API_key = os.getenv("API_key")
bot.run(os.getenv('TOKEN'))
