import asyncio
import random
import pickle

BUFFERSIZE = 512

outgoing = []

class Player:
    def __init__(self, ownerid, pear):
        self.move = "None"
        self.ownerid = ownerid
        self.pearname = pear

minionmap = {}

def updateWorld(message):
    arr = pickle.loads(message)
    print(str(arr))
    playerid = arr[1]
    move = arr[2]

    if playerid == 0:
        return

    minionmap[playerid].move = move

    remove = []

    for i in outgoing:
        update = [arr[0]]

        update.append([playerid, minionmap[playerid].move])

        try:
            i.write(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        print('Sent update data')

    for r in remove:
        outgoing.remove(r)

class MainServer(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print(f'Connection address: {peername[0]} {peername[1]}')
        # Store the transport object as an instance variable
        self.transport = transport  
        outgoing.append(transport)
        for id in range(1, 11):
            try:
                minionmap[id]
            except:
                playerid = id
                break

        playerminion = Player(playerid, transport.get_extra_info('peername')[1])
        minionmap[playerid] = playerminion
        print(playerid)
        transport.write(pickle.dumps(['id update', playerid]))

    def data_received(self, data):
        receivedData = data
        if receivedData:
            updateWorld(receivedData)
        else:
            self.transport.close()

    def connection_lost(self, exc):
        removed = False
        copy = minionmap.copy()
        for key, value in copy.items():
            if value.pearname == self.transport.get_extra_info('peername')[1]:
                del minionmap[key]
                last_key = key
                removed = True
                print(f"Player {value.ownerid} disconnected")
            elif removed:
                minionmap[last_key] = minionmap[key]
                del minionmap[key]
                self.transport.write(pickle.dumps(['id update', last_key]))
                last_key = key



        # print(minionmap)

        outgoing.remove(self.transport)

class SecondaryServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        pass

    def connection_lost(self, exc):
        pass

async def main():
    loop = asyncio.get_running_loop()
    server = await loop.create_server(MainServer, '', 4321)

    async with server:
        await server.serve_forever()

asyncio.run(main())
