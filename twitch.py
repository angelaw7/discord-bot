import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
twitch_app_token_json = {}
twitch_user = ''
image_priority = 'Preview'
stream_api_url = "https://api.twitch.tv/helix/streams"
stream_url = "https://www.twitch.tv/" + twitch_user.lower()
DISCORD_URL = os.getenv("DISCORD_URL")
discord_message = ''
discord_description = ''


def authorize():
    token_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
    }
    app_token_request = requests.post('https://id.twitch.tv/oauth2/token', params=token_params)
    global twitch_app_token_json
    twitch_app_token_json = app_token_request.json()


def main(streamer):
    global twitch_user
    twitch_user = streamer
    authorize()
    twitch_json = {'data': []}

    while len(twitch_json['data']) == 0:
        twitch_headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': 'Bearer ' + twitch_app_token_json['access_token'],
        }
        twitch_params = {'user_login': twitch_user.lower()}
        request_status = 401
        while request_status == 401:
            twitch_request = requests.get(stream_api_url, headers=twitch_headers, params=twitch_params)
            request_status = twitch_request.status_code
            if request_status == 401:
                authorize()
                twitch_headers['Authorization'] = 'Bearer ' + twitch_app_token_json['access_token']
                continue
            twitch_json = twitch_request.json()

        if len(twitch_json['data']) == 1:
            print("Stream is live.")

            stream_json = twitch_json['data'][0]
            stream_title = stream_json['title']
            stream_game_id = stream_json['game_id']
            stream_preview_temp = stream_json['thumbnail_url']
            stream_preview_temp = stream_preview_temp.replace('{width}', '1280')
            stream_preview_temp = stream_preview_temp.replace('{height}', '720')
            preview_request = requests.get(stream_preview_temp)
            if '404' not in preview_request.url:
                stream_preview = stream_preview_temp
            else:
                stream_preview = None

            game_search_url = "https://api.twitch.tv/helix/games"
            game_params = {'id': stream_game_id}
            search_response = {}
            request_status = 401
            while request_status == 401:
                game_request = requests.get(game_search_url, headers=twitch_headers, params=game_params)
                request_status = game_request.status_code
                if request_status == 401:
                    authorize()
                    twitch_headers['Authorization'] = 'Bearer ' + twitch_app_token_json['access_token']
                    continue
                search_response = game_request.json()

            stream_game = "something"
            game_logo = None
            if len(search_response['data']) > 0:
                game_data = search_response['data'][0]
                stream_game = game_data['name']
                game_logo_temp = game_data['box_art_url']
                game_logo_temp = game_logo_temp.replace('{width}', '340')
                game_logo_temp = game_logo_temp.replace('{height}', '452')
                logo_request = requests.get(game_logo_temp)
                if '404' not in logo_request.url:
                    # Scrub ./ from the boxart URL if present so it works with the Discord API properly
                    game_logo = game_logo_temp.replace('./', '')

            user_search_url = "https://api.twitch.tv/helix/users"
            user_params = {'login': twitch_user.lower()}
            user_response = {}
            request_status = 401
            while request_status == 401:
                user_request = requests.get(user_search_url, headers=twitch_headers, params=user_params)
                request_status = user_request.status_code
                if request_status == 401:
                    authorize()
                    twitch_headers['Authorization'] = 'Bearer ' + twitch_app_token_json['access_token']
                    continue
                user_response = user_request.json()

            user_logo = None
            print(str(user_response))
            if len(user_response['data']) == 1:
                user_data = user_response['data'][0]
                user_logo_temp = user_data['profile_image_url']
                logo_request = requests.get(user_logo_temp)
                if '404' not in logo_request.url:
                    # Scrub ./ from the boxart URL if present so it works with the Discord API properly
                    user_logo = user_logo_temp.replace('./', '')

            global discord_description
            discord_description = twitch_user + " is playing " + stream_game + " :D"
            global discord_message
            discord_message = discord_message.replace('{{Name}}', twitch_user)
            discord_message = discord_message.replace('{{Game}}', stream_game)

            if image_priority == "Game":
                if game_logo:
                    stream_logo = game_logo
                else:
                    if stream_preview:
                        stream_logo = stream_preview
                    else:
                        stream_logo = user_logo
            else:
                if stream_preview:
                    stream_logo = stream_preview
                else:
                    if game_logo:
                        stream_logo = game_logo
                    else:
                        stream_logo = user_logo

            discord_payload = {
                "embeds": [
                    {
                        "title": stream_title,
                        "url": stream_url,
                        "description": discord_description,
                        "image": {
                            "url": stream_logo
                        }
                     }
                ]
            }

            status_code = 0
            while status_code != 204:
                discord_request = requests.post(DISCORD_URL, json=discord_payload)
                status_code = discord_request.status_code

                if discord_request.status_code == 204:
                    print("Successfully called Discord API. Waiting 5 seconds to terminate...")
                    time.sleep(5)
                else:
                    print("Failed to call Discord API. Waiting 5 seconds to retry...")
                    time.sleep(5)
        else:
            discord_payload = {
              "content": 'Stream not live :<',
            }
            discord_request = requests.post(DISCORD_URL, json=discord_payload)
            status_code = discord_request.status_code

            return
