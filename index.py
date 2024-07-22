from flask import Flask, jsonify, request
from database.database import database
from controllers.ClockController import ClockController
import threading
import socket


app = Flask(__name__)

@app.route('/sync', methods=['GET'])
def syncronize():
    global database
    for clock in database['clocks']:

        # Conferindo se esse relógio é líder, se não for, comparamos com o líder:
        if clock['isLeader']:

            # Atualizando relógio atual geral.
            database['time'] = clock['time']
            break

    # Atualizando relógio atual na lista de relógios do sistema:
    for clock in database['clocks']:
        clock['time'] = database['time']

    return jsonify({'message': 'Relógios sincronizados!', 'time': database['time']}), 201

@app.route('/leaderIsThere', methods=['GET'])
def verify():
    return jsonify({'message': 'Online!'}), 201

def incrementThread():
    ClockController.incrementAndSendTime()


def receiveOthersTime():
    ClockController.showClocksInfo()


def showClocks():
    ClockController.receiveOthersTime()

def checkLeaderIsThere():
    ClockController.checkLeaderIsThere()

if __name__ == '__main__':
    print('Realize a configuração prévia do relógio:')

    apiPort = int(input('Insira a porta da API: '))
    udpPort = int(input('Insira a porta UDP: '))
    drift = float(input('Insira o drift: '))

    database['drift'] = drift
    database['udpPort'] = udpPort

    udpTransmitter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udpListenner = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpListenner.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
    udpListenner.bind(('0.0.0.0', database['udpPort']))

    database['udpTransmitter'] = udpTransmitter
    database['udpListenner'] = udpListenner

    increment_thread = threading.Thread(target=incrementThread, daemon=True)
    increment_thread.start()

    receive_others_time = threading.Thread(target=receiveOthersTime, daemon=True)
    receive_others_time.start()

    thread_checkLeaderIsThere = threading.Thread(target=checkLeaderIsThere, daemon=True)
    thread_checkLeaderIsThere.start()

    show_clocks = threading.Thread(target=showClocks, daemon=True)
    show_clocks.start()

    app.run(debug=False, port=apiPort)