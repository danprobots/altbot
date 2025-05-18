# AltBot
A simple project that turns your bot into (kind of) an account.

⚠️ If you came here to setup your alt and don't want to host it yourself, please **type */clone* into [our Telegram bot](https://t.me/SamyarT2bot)** to get it running fast and simple.
ℹ️ *Note: This version doesn't support cloning.*

# Installation
Let's clone the repository.
```
git clone https://github.com/danprobots/altbot.git
```
Now, let's install the dependencies.
```
pip install -r requirements.txt
```
Then, configure the variables in the script.
```
bot_token = "" # your token goes here
api_id = 'API_ID_HERE' # check this on how to get them: https://core.telegram.org/api/obtaining_api_id
api_hash = 'API_HASH_HERE' # if you wont fill in these info, your bot CANNOT change its pfp on its own.
alt_owner_username = "yourusernamehere" # replace with the ALT owner's username
start_message = """
Hi there, i'm an awesome alt!
""" # replace this with WHAT the bot should say on /start (supports multi-lines)
```
Finally, run the bot.
```
python alt.py
```

# Contact me
You can contact me [on Telegram](https://t.me/danielprofessional) or via my email.

⭐ Make sure to give this project a star for more updates!
