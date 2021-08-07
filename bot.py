#!/usr/bin/python3

import os
import random
import requests
import websockets
import asyncio
import json

import discord
from discord.ext import commands

from dotenv import load_dotenv

"""
TODO:
     If bot is global/public
         Lock websocket monitor user down
         Only allow user to add themselves to the registered/DNS name list
         Figure out how to route messages to specific users
     Private Bot
         Whatever
    
"""

#get os env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


#my two nodes. This dict grows with the '!bolt register <user> <pubkey>' command. Serves as janky DNS like storage
users = {
"skid1":"030b767818f3eb5dbc4bf6c514a6793104aaa381dbe3c65f6441272422fea1564d",
"skid2":"034c39a618a0e65598eda2633479e718c94a36b9a797170dca27e8d5a39dfdf118"
}


#placeholder variables
userSubscriptionID = None
userSubscriptionObject = None



#allow discord to query user information
intents = discord.Intents.default()
intents.members = True

#create bot object
bot = commands.Bot(command_prefix='!bolt ', intents=intents)

#monitor websocket when not handling a command
@bot.event
async def on_ready():
    async with websockets.connect('ws://localhost:8884/v1/subscribe') as websocket: #this is my second node (skid2)
        while True:
            try:
                print("Waiting for websocket events on skid2!")
                message = await websocket.recv()
                print(message) #debug message info
                print(userSubscriptionObject) #debug '!bolt subscribe' user info (replying to this user with incomming ws info...)
                if (userSubscriptionObject):
                    msg = json.loads(message)['result']['data'] #grab message from incomming message
                    pubkey = json.loads(message)['result']['fromPubkey'] #grab sender public key from message
                    for key, value in users.items(): #check to see if we are already tracking this pubkey/user
                        if pubkey == value:
                            pubkey = key
                    await userSubscriptionObject.send("Incomming Message from Websocket! \n" + "From PublicKey/User: " + pubkey + "\n" + "Message: " + msg)

            except websockets.exceptions.ConnectionClosed:
                print('ConnectionClosed')
                is_alive = False
                break

                
#set up bot command to handle sending messages via my first node (skid1). #users are managed by bot user (need to verify calling user to prevent registration issues)

@bot.command(name='message', help='Sends a message via the IMPERVIOUS API! !bolt message <msg> <pubkey/username>')
async def message(ctx, msg, pubkey):

    headers = {'Content-Type': 'application/json'}

    if (pubkey in users): #check to see if provided name is registered with us
        pubkey = users[pubkey] #grab pubkey of provided user if present
        
    req = requests.post('http://127.0.0.1:8882/v1/message/send', json={"msg":msg, "pubkey":pubkey}, headers=headers)
    res = req.text
    
    await ctx.send("Message Sent. Awaiting your command! " + res)
    

#create bot command to register usernames instead of keeping track of publickeys
@bot.command(name='register', help='DNS for your name and public key! !bolt register <user> <pubkey>')
async def message(ctx, user, pubkey):

    print(ctx.author.name)

    users[user] = pubkey
    print(users)

    await ctx.send("Added user to registry!")


#this will DM whatever users hits it with incomming websocket messages. Right now only 1 user can subscribe and obviously we dont want any rando to monitor the websocket
@bot.command(name='subscribe', help='Subscribe to receive notifications from the websocket!')
async def subscribe(ctx):

    global userSubscriptionID
    userSubscriptionID = ctx.message.author.id
    global userSubscriptionObject
    userSubscriptionObject = bot.get_user(int(userSubscriptionID))
    
    print(userSubscriptionID)
    print(userSubscriptionObject)
    
    await ctx.send("Subscribed for websocket updates! UserID: " + str(userSubscriptionID))


bot.run(TOKEN)

