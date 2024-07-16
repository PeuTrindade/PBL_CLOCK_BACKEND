from database.database import database
import time
import json

class ClockController:
    @staticmethod
    def increment():
        while True:
            time.sleep(database['drift'])

            database['time'] += 1


    @staticmethod
    def receiveOthersTime():
        while True:
            message, address = database['udpListenner'].recvfrom(4096)
            time = json.loads(message.decode())

            print(f"Tempo recebido: {time}!")

    
    @staticmethod
    def sendCurrentTime():
        while True:
            for clock in database['clocks']:
                if clock['udpPort'] != database['udpPort']:
                    database['udpTransmitter'].sendto(json.dumps(database['time']).encode(), (clock['clock'], int(clock['udpPort'])))

                    print(f"Tempo atual enviado para {clock['clock']}:{clock['udpPort']}!")
