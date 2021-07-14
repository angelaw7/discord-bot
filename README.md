# Discord Bot
A Discord bot made for fun :)

## Commands
- sa \<anime title\>: search an anime title
  
  ![Example of Search Anime command on Toradora](https://user-images.githubusercontent.com/74735037/125562489-9c9b2fda-2a27-41ab-9d67-33bc29d85087.png)

- sr \<summoner name\>: search a League summoner's ranked stats and top champions

  ![Example of Summoner Rank command on Doublelift](https://user-images.githubusercontent.com/74735037/125562533-66d8bd17-9185-45cf-a9c9-c21b8e2e6a7c.png)

- ud \<word to search\>: search a term on Urban Dictionary
 
  ![Example of Urban Dictionary command searching cat](https://user-images.githubusercontent.com/74735037/125562417-d7893e2b-d2ae-4519-b63e-6b338736e370.png)

- stream \<streamer name\>: search whether a Twitch Streamer is live
- cf: coin flip
- purge \<# messages to purge\>: removes # of messages from current channel

## Get Started
1. Clone the repo
```sh
https://github.com/angelaw7/discord-bot.git
```

2. (Optional) Get a [Twitch Client ID + Secret](https://dev.twitch.tv/docs/api/) and a [Riot API Key](https://developer.riotgames.com/)
3. Get a [Discord Bot Token](https://dev.twitch.tv/docs/api/) and Discord Webhook (optional for Twitch command)
4. Enter all data in a .env file, following example.env
5. Install dependencies and run main.py
```sh
pip install -r requirements.txt
python main.py
```
