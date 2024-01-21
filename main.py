from pyrogram import Client, filters
import requests
import time
import schedule

# Replace these placeholders with your actual values
api_token = "5638291199:AAHo4XByOwWaNuS6XPaJXVPMEKjeSrBSaAs"
YOUR_API_HASH = "31ee7eb1bf2139d96a1147f3553e0364"
YOUR_API_ID = "12997033"
MAL_CLIENT_ID = "2908e56984945af7acdac6951d87eb3a"
MAL_CLIENT_SECRET = "4337e3fe1323d4b23c6f59f85c9e6c79484b446ec7845f81b2b2eda5d9ff89af"
MAL_USERNAME = "syblewiliiam"
MAL_PASSWORD = "amanpathan123#"
OWNER_ID = 1352973730

bot = Client("anime_news_bot", api_id=YOUR_API_ID, api_hash=YOUR_API_HASH, bot_token=api_token)


def get_mal_access_token():
    mal_auth_url = "https://myanimelist.net/v1/oauth2/token"
    data = {
        "client_id": MAL_CLIENT_ID,
        "client_secret": MAL_CLIENT_SECRET,
        "grant_type": "password",
        "username": MAL_USERNAME,
        "password": MAL_PASSWORD
    }
    try:
        response = requests.post(mal_auth_url, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        print(f"Error obtaining MAL API access token: {e}")
        return None


def fetch_mal_anime_news(access_token):
    mal_news_url = "https://api.myanimelist.net/v2/anime/news"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(mal_news_url, headers=headers)
        response.raise_for_status()
        return response.json().get("data")
    except requests.RequestException as e:
        print(f"Error fetching MAL anime news: {e}")
        return None


def post_news_to_chat(chat_id, news, source):
    for article in news:
        try:
            news_message = f"📰 {source} - {article['title']}\n\n{article['intro']}"
            image_url = article.get("image_url")

            if image_url:
                bot.send_photo(chat_id, photo=image_url, caption=news_message)
            else:
                bot.send_message(chat_id, text=news_message)

            time.sleep(2)  # To avoid rate limiting, adjust delay if needed
        except Exception as e:
            print(f"Error posting news to chat {chat_id}: {e}")


def get_all_chat_ids(bot):
    try:
        # Get the list of all chats where the bot is a member
        all_chats = list(bot.iter_dialogs())
        chat_ids = [chat.chat.id for chat in all_chats]
        return chat_ids
    except Exception as e:
        print(f"Error fetching chat IDs: {e}")
        return []


def check_mal_news():
    mal_access_token = get_mal_access_token()

    if mal_access_token:
        mal_news = fetch_mal_anime_news(mal_access_token)
        if mal_news:
            all_chat_ids = get_all_chat_ids(bot)
            for chat_id in all_chat_ids:
                post_news_to_chat(chat_id, mal_news, "MyAnimeList")
    else:
        print("Failed to get MAL API access token.")


# Schedule the job to run every 2 minutes for testing; adjust as needed
schedule.every(10).minutes.do(check_mal_news)


@bot.on_message(filters.command("start"))
def start_command_handler(_, message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, "Welcome to the Anime News Bot! I'll keep you updated with the latest anime news.\n"
                                   "Use /help to see available commands.")
    except Exception as e:
        print(f"Error sending start message to chat {chat_id}: {e}")


@bot.on_message(filters.command("help"))
def help_command_handler(_, message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, "This bot provides the latest anime news from MyAnimeList.\n\n"
                                   "Available commands:\n"
                                   "/start - Start the bot\n"
                                   "/help - Display this help message\n"
                                   "**if you have any questions regarding bot ,Feel Free to contact @AmaNuh **")
    except Exception as e:
        print(f"Error sending help message to chat {chat_id}: {e}")


if __name__ == "__main__":
    try:
        # Run the bot
        print("Bot is running")
        bot.run()
    except Exception as e:
        print(f"Error running the bot: {e}")

