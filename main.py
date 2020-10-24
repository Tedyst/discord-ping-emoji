import asyncio
import json
import os
import re

import discord
import emoji
from dotenv import load_dotenv

load_dotenv()

db = {}


def filesave():
    with open('data.txt', 'w') as outfile:
        json.dump(db, outfile)


try:
    with open('data.txt') as json_file:
        data = json.load(json_file)
        if data:
            db = data
except:
    filesave()


def custom_emoji(client, message):
    custom_emoji_id = int(message.split(':')[
        2].replace('>', ''))
    custom_emoji_id = client.get_emoji(custom_emoji_id)
    if custom_emoji_id is None:
        return None
    return message


def native_emoji(client, message):
    if emoji.emoji_count(message) == 1:
        return message
    return None


def used_emoji(client, message):
    return native_emoji(client, message) or custom_emoji(client, message)


class Ping(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: discord.Message):
        if message.content.startswith('ping '):
            content = message.content.split(' ')[1:]
            if content[0] == "set":
                if len(content) != 2:
                    await message.channel.send("Not valid arguments")
                    return
                used = used_emoji(self, content[1])
                if used is None:
                    await message.channel.send("Not valid emoji")
                if used not in db:
                    db[used] = {
                        "people": []
                    }
                for emojis in db:
                    if message.author.id in db[emojis]["people"]:
                        db[emojis]["people"].remove(message.author.id)
                db[used]["people"].append(message.author.id)
                print(db)
                filesave()
            if content[0] == "clear":
                for emojis in db:
                    if message.author.id in db[emojis]["people"]:
                        db[emojis]["people"].remove(message.author.id)
                await message.channel.send("Cleared")
                filesave()
            if content[0] == "help":
                await message.channel.send("ping set <emoji> / ping clear")

    async def on_reaction_add(self, reaction, user):
        print(reaction)
        message = None
        if reaction.custom_emoji == False:
            message = reaction.emoji
        else:
            message = "<:{}:{}>".format(reaction.emoji.name, reaction.emoji.id)
        if message in db:
            response = ""
            for person in db[message]["people"]:
                response += '<@{}> '.format(person)
            if response != "":
                response = await reaction.message.channel.send(response)
            await asyncio.sleep(20)
            await response.delete()


client = Ping()
client.run(os.getenv('TOKEN'))
