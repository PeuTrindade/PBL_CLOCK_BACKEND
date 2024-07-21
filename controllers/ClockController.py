from database.database import database
import time
import json
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
        # ===============================================================================================

                    # Seguindo o tempo do líder:

                    # for clock in database['clocks']:

                    #     # Conferindo se esse relógio é líder, se não for, comparamos com o líder:
                    #     if clock['isLeader'] and clock['clock'] == address[0]:

                    #         # Comparando os tempos entre esse relógio atual e o líder:
                    #         if time > database['time']:

                    #             # Atualizando relógio atual geral.
                    #             database['time'] = time

                    #             # Atualizando relógio atual na lista de relógios do sistema:
                    #             for clock in database['clocks']:
                    #                 if clock['udpPort'] == database['udpPort']:
                    #                     clock['time'] = database['time']
                    #                     break

    @staticmethod
    def showClocksInfo():
        global database

        while True:
            time.sleep(0.1)
            os.system('clear')
            
            print('=============================================')
            for clock in database['clocks']:
                if clock['isLeader'] == True:
                    print(f"Relógio (Líder): {clock['clock']}:{clock['udpPort']}\nHora: {clock['time']}")
                else:
                    print(f"Relógio: {clock['clock']}:{clock['udpPort']}\nHora: {clock['time']}")

                print('=============================================')
