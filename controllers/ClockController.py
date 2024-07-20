from database.database import database
import time
import json

class ClockController:
    @staticmethod
    def increment():
        global database
        while True:
            time.sleep(database['drift'])

            database['time'] += 1

            for clock in database['clocks']:
                if clock['udpPort'] != database['udpPort']:
                    database['udpTransmitter'].sendto(json.dumps(database['time']).encode(), (clock['clock'], int(clock['udpPort'])))

                    print(f"Tempo atual enviado para {clock['clock']}:{clock['udpPort']}!")


    @staticmethod
    def receiveOthersTime():
        global database
        while True:
            message, address = database['udpListenner'].recvfrom(4096)
            time = json.loads(message.decode())

            # Inserindo informações recebidas no database:
            for clock in database['clocks']:
                if clock['clock'] == address[0]:
                    clock['time'] = time
                    break
            
            print(database)

            print(f"Tempo recebido: {time}!")
