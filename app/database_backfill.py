import pickle
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest

api_id = '24687616'
api_hash = '8a341c62db466e4cac2c74f18c476d09'
phone_number = "+18135031020"


def get_messages():
    client = TelegramClient('session_name', api_id, api_hash)

    async def fetch_channel_messages(channel_username):
        await client.start()

        # If 2FA is enabled, handle password prompt
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            try:
                await client.sign_in(phone_number, input('Enter the code: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Password: '))

        # Step 3: Get the channel by username
        channel = await client.get_entity(channel_username)

        # Step 4: Fetch all the messages from the channel
        offset_id = 0
        limit = 100
        all_messages = []

        while True:
            history = await client(GetHistoryRequest(
                peer=channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break

            messages = history.messages
            all_messages.extend(messages)
            offset_id = messages[-1].id  # Update the offset_id to the last message ID

        return all_messages

    # Step 5: Run the async function to get messages
    with client:
        messages = client.loop.run_until_complete(fetch_channel_messages('mindvirusfeed'))

    with open("backfill_data.pkl", "wb") as save:
        pickle.dump(messages, save)

    print(len(messages))


with open("backfill_data.pkl", "rb") as f:
    messages = pickle.load(f)

for message in messages:
    print(message)
    input()

