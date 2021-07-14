import json
import urllib.request
import requests

with urllib.request.urlopen("http://ddragon.leagueoflegends.com/cdn/10.25.1/data/en_US/champion.json") as url:
    champion_data = json.loads(url.read().decode())


def request_summoner_data(summoner_name, API_key):
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name + "?api_key=" + API_key
    response = requests.get(URL)
    return response.json()


def request_ranked_data(ID, API_key):
    URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + ID + "?api_key=" + API_key
    response = requests.get(URL)
    return response.json()


def request_top_champs(ID, API_key):
    URL = "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + ID + "?api_key=" + API_key
    response = requests.get(URL)
    return response.json()


def id_to_champ(champ_ID):
    for i in champion_data["data"]:
        for j in champion_data["data"][i]:
            if j == "key":
                if champion_data["data"][i]["key"] == champ_ID:
                    return i


def request_live_match(ID, API_key):
    URL = "https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/" + ID + "?api_key=" + API_key
    response = requests.get(URL)
    return response.json()
    