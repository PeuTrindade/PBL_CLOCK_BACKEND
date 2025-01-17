from database.database import database
import time
import json
import requests
import os

class ClockController:
    @staticmethod
    def incrementAndSendTime():
        global database
        while True:

            # Simulação da contagem do tempo:
            time.sleep(database['drift'])

            # Atualizando relógio atual geral.
            database['time'] += 1

            # Atualizando relógio atual na lista de relógios do sistema:
            for clock in database['clocks']:
                if clock['udpPort'] == database['udpPort']:
                    clock['time'] = database['time']

            # Verificando líder atual:
            max_time = max(range(len(database['clocks'])), key=lambda i: database['clocks'][i]['time'])
            
            # Definir isLeader=True para o objeto com o maior 'time' e False para os outros
            for i, clock in enumerate(database['clocks']):
                if i == max_time:
                    clock['isLeader'] = True
                else:
                    clock['isLeader'] = False

            # Enviando tempos para outros relógios:
            for clock in database['clocks']:
                if clock['udpPort'] != database['udpPort']:
                    database['udpTransmitter'].sendto(json.dumps(database['clocks']).encode(), (clock['clock'], int(clock['udpPort'])))

    @staticmethod
    def receiveOthersTime():
        global database
        while True:
            message, address = database['udpListenner'].recvfrom(4096)
            decoded_message = json.loads(message.decode())
            database['clocks'] = decoded_message
    
    @staticmethod
    def checkLeaderIsThere():
        global database
        while True:
            time.sleep(2)
            for clock in database['clocks']:
                if clock['isLeader'] and clock['udpPort'] != database['udpPort']:
                    try:
                        getReturn = requests.get(f'http://{clock['clock']}:{clock['apiPort']}/leaderIsThere').status_code

                        if getReturn == 200:
                            clock['time'] = 0
                    except:
                        clock['time'] = 0

    @staticmethod
    def showClocksInfo():
        global database

        while True:
            time.sleep(0.1)
            if os.name == 'posix':
                os.system('clear')  
            elif os.name == 'nt': 
                os.system('cls')
            
            print('=============================================')
            for clock in database['clocks']:
                if clock['isLeader'] == True:
                    print(f"Relógio (Líder): {clock['clock']}:{clock['udpPort']}\nHora: {clock['time']}")
                else:
                    print(f"Relógio: {clock['clock']}:{clock['udpPort']}\nHora: {clock['time']}")

                print('=============================================')
