from database.database import database
import time
import json

class ClockController:
    @staticmethod
    def incrementAndSendTime():
        global database
        while True:

            # Simulação da contagem do tempo:
            time.sleep(database['drift'])

            # Contagem do tempo caso não esteja sincronizado:
            for clock in database['clocks']:
                if clock['isLeader']:
                    if clock['time'] != database['time']:

                        # Atualizando relógio atual geral caso não esteja sincronizado:
                        database['time'] += 1

            # Atualizando relógio atual na lista de relógios do sistema:
            for clock in database['clocks']:
                if clock['udpPort'] == database['udpPort']:
                    clock['time'] = database['time']

            # Enviando tempo para outros relógios:
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

# ===============================================================================================

            # Sincronização com o líder:

            for clock in database['clocks']:

                # Conferindo se esse relógio é líder, se não for, comparamos com o líder:
                if clock['isLeader'] and clock['clock'] == address[0]:

                    # Comparando os tempos entre esse relógio atual e o líder:
                    if time > database['time']:

                        # Atualizando relógio atual geral.
                        database['time'] = time

                        # Atualizando relógio atual na lista de relógios do sistema:
                        for clock in database['clocks']:
                            if clock['udpPort'] == database['udpPort']:
                                clock['time'] = database['time']
                                break

# ===============================================================================================

            # Inserindo informações recebidas no database:
            for clock in database['clocks']:
                if clock['clock'] == address[0]:
                    clock['time'] = time
                    break
            
            print(database)

            print(f"Tempo recebido: {time}!")
