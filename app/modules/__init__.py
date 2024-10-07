import os
from dotenv import load_dotenv
# Get the path to the .env file, two levels up
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')

load_dotenv(dotenv_path)




############################################################################
# Environment Variables + Setup

api_token = os.getenv('API_KEY')
# chan_id = int(os.getenv('DEV_ID'))
chan_id = int(os.getenv('DEST_CHAN_ID'))

# Replace 'YOUR_BOT_TOKEN' with the token you get from BotFather
TOKEN = api_token
# Replace 'DESTINATION_CHANNEL_ID' with the ID of @mindvirusfeed channel
DESTINATION_CHANNEL_ID = chan_id

############################################################################


