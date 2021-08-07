#!/usr/bin/python3

from websocket import create_connection


ws = create_connection("ws://localhost:8884/v1/subscribe")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
