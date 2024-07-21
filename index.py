from flask import Flask, jsonify, request
from database.database import database
from controllers.ClockController import ClockController
import threading
import socket


app = Flask(__name__)


def incrementThread():
    ClockController.incrementAndSendTime()


def receiveOthersTime():
    ClockController.showClocksInfo()


def showClocks():
    ClockController.receiveOthersTime()


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

    show_clocks = threading.Thread(target=showClocks, daemon=True)
    show_clocks.start()

    app.run(debug=False, port=apiPort)