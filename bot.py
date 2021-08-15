#!/usr/bin/python3

import os
import random
import requests
import websockets
import asyncio
import json
import pprint

import discord
from discord.ext import commands

from dotenv import load_dotenv

"""
TODO:
     If bot is global
         n/a

"""

#get os env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


#my two nodes. This dict grows with the '!bolt register <user> <pubkey>' command. Serves as janky DNS like storage
global subscribedUsers
subscribedUsers = {}

global localNode
localNode = '034c39a618a0e65598eda2633479e718c94a36b9a797170dca27e8d5a39dfdf118'


global headers
headers = {'Content-Type': 'application/json'}




#allow discord to query user information
intents = discord.Intents.default()
intents.members = True

#create bot object
bot = commands.Bot(command_prefix='!bolt ', intents=intents)

#monitor websocket when not handling a command
@bot.event
async def on_ready():
    async with websockets.connect('ws://localhost:8884/v1/subscribe') as websocket: #this is my second node (airmonster2)
        while True:
            try:
                print("Waiting for websocket events on airmonster2!")
                message = await websocket.recv()
                print(message) #debug message info

                msg = json.loads(message)['result']['data'] #grab message from incomming message
                discordUser = msg.split(':bolt:')[0] ##discord username to lookup
                discordUserMessage = msg.split(':bolt:')[1] #message

                pubkey = json.loads(message)['result']['fromPubkey'] #grab sender public key from message



                for key, value in subscribedUsers.items(): #check to see if we are already tracking this pubkey/user
                    if pubkey == value:
                        pubkey = bot.get_user(key[1])

                for key in subscribedUsers:
                    resolvedUser = bot.get_user(key[1])
                    if str(resolvedUser) == discordUser:
                        await resolvedUser.send("Incomming Message from Websocket! \n" + "From PublicKey/User: " + pubkey + "\n" + "Message: " + discordUserMessage)
                        await resolvedUser.send(file=discord.File(r'/home/lightning/Downloads/test.png'))



            except KeyError:
                print("Key Error: User not subscribed")
                continue
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break
            
            except:
                print("Other exception")
                continue
            

              
#set up bot command to handle sending messages via my first node (skid1). #users are managed by bot user (need to verify calling user to prevent registration issues)
@bot.command(name='message', help='Sends a message via the IMPERVIOUS API! !bolt message <msg> <pubkey/username>')
async def message(ctx, msg, pubkey):

    
    for key, value in subscribedUsers.items(): #check to see if we are already tracking this pubkey/user
        if pubkey == key[0]:
            pubkey = value

    if (pubkey in subscribedUsers): #check to see if provided name is registered with us
        pubkey = subscribedUsers[pubkey] #grab pubkey of provided user if present
        
    req = requests.post('http://127.0.0.1:8882/v1/message/send', json={"msg":msg, "pubkey":pubkey}, headers=headers)
    res = req.text
    
    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)

    await ctx.send("Processing...Check your DMs...")

    await userSubscriptionObject.send("Message Sent. Awaiting your command! " + res)




'''
#create bot command to register usernames instead of keeping track of publickeys
@bot.command(name='register', help='DNS for your name and public key! Running "!bolt register <pubkey>" will add your discord username#1337 to the pubkey registry')
async def message(ctx, pubkey):

    registeredUsers[str(ctx.message.author)] = pubkey

    await ctx.send("Added " + str(ctx.message.author) + " to the registry!")


    print(registeredUsers)
'''


#create bot command to list current registry
@bot.command(name='registryList', help='List all those that have registered')
async def message(ctx):

    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)

    await ctx.send("Processing...Check your DMs...")

    await userSubscriptionObject.send("Current Registry:\n```" + str(pprint.pformat(subscribedUsers)) + "```")


    print(subscribedUsers)






@bot.command(name='sign', help='Sign a message with private key. !bolt sign "message"')
async def sign(ctx, message):

    req = requests.post('http://127.0.0.1:8882/v1/sign', json={"msg":message}, headers=headers)
    res = req.text

    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)

    await ctx.send("Processing...Check your DMs...")

    await userSubscriptionObject.send("Signed message response: \n```" + res + "```")






@bot.command(name='verify', help='Verify a signed message. !bolt verify <message> <sig>')
async def verify(ctx, message, sig):

    req = requests.post('http://127.0.0.1:8882/v1/verify', json={"msg":message, "signature":sig}, headers=headers)
    res = req.text

    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)

    await ctx.send("Processing...Check your DMs...")

    await userSubscriptionObject.send("Verification result: \n```" + res + "```")


@bot.command(name='vpnQuote', help='Ask for quote and begin vpn services with remote node. !bolt vpnQuote <pubkey/registered name>')
async def vpnQuote(ctx, pubkey):

    req = requests.post('http://127.0.0.1:8884/v1/vpn/quote',json={"pubkey":pubkey}, headers=headers)
    res = req.text

    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)

    await ctx.send("Processing...Check your DMs...")

    await userSubscriptionObject.send("Still in development... " + res)


@bot.command(name='vpnRequest', help='Agree to the VPN terms and get your config. !bolt vpnRequest <pubkey/registered name> <nonce> <price>')
async def vpnRequest(ctx, pubkey, nonce, price):

    req = requests.post('http://127.0.0.1:8884/v1/vpn/contract',json={"pubkey":pubkey, "nonce":nonce, "price":price}, headers=headers)
    res = req.text

    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)

    await ctx.send("Processing...Check your DMs...")

    await userSubscriptionObject.send("Still in development... " +  res)    




#this will sign discord users up for notifications via /v1/message/send
@bot.command(name='subscribe', help='Subscribe to receive notifications from the websocket! !bolt subscribe <pubkey>')
async def subscribe(ctx, pubkey):


    userSubscriptionID = ctx.message.author.id #get the raw, global user id
    userSubscriptionObject = bot.get_user(int(userSubscriptionID)) #turn global user id into friendly discord id (e.g. username#1337)
    
    print(userSubscriptionID) #debug
    print(userSubscriptionObject) #debug

    subscribedUsers[(str(userSubscriptionObject), userSubscriptionObject.id)] = pubkey
    print(subscribedUsers) #debut

    await ctx.send("Processing.... check your DMs...")
    
    await userSubscriptionObject.send('''Subscribed for websocket updates! UserID: ''' + str(userSubscriptionObject) + '''! Tell your sender to format their IMP messages to you in the following format: \n\n```POST /v1/message/send\n\n{\n\t"msg":"''' + str(userSubscriptionObject) + ''':bolt:Hello there!",\n\t"pubkey":"''' + str(localNode) + '''"\n}``` ''')


 
    


bot.run(TOKEN) #start the bot
