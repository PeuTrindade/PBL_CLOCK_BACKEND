import socket
import threading
import time
import pickle

# Variável global para o contador de tempo e endereço do líder
time_counter = 0
leader_address = ('localhost', 3030)
lock = threading.Lock()
is_leader = False
clients = set()
sync = True

# Função para incrementar o contador de tempo
def increment_time(delay):
    global time_counter
    while True:
        with lock:
            time_counter += 1
        time.sleep(delay)

# Função para sincronizar com o líder
def sync_with_leader():
    global time_counter, leader_address, is_leader
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if not is_leader:
            sock.sendto(pickle.dumps('SYNC'), leader_address)
            data, addr = sock.recvfrom(1024)
            message = data.decode()
            print(message)

            if message.startswith('NEW_LEADER'):
                new_leader_ip, new_leader_port = message.split()[1:]
                leader_address = (new_leader_ip, int(new_leader_port))
            else:
                leader_time = int(message)
                with lock:
                    if leader_time > time_counter:
                        time_counter = leader_time
                    elif time_counter > leader_time:
                        sock.sendto(f'NEW_LEADER {time_counter}'.encode(), leader_address)
        time.sleep(5)

def transmitterSyncMessage():
    global time_counter, leader_address, is_leader, sync
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
      if not is_leader and sync:
        sock.sendto(pickle.dumps('SYNC'), leader_address)


# Função para o servidor UDP
def udp_server(host='localhost', port=3030):
    global time_counter, leader_address, is_leader
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        print(message)

        if message == 'SYNC':
            if is_leader:
                with lock:
                    sock.sendto(str(time_counter).encode(), addr)
                    clients.add(addr)  # Adiciona o cliente à lista de clientes conhecidos
        elif message.startswith('NEW_LEADER'):
            new_time = int(message.split()[1])
            with lock:
                if new_time > time_counter:
                    time_counter = new_time
                    leader_address = addr
                    is_leader = False
                    notify_clients_of_new_leader(sock, addr)

# Função para notificar todos os clientes sobre o novo líder
def notify_clients_of_new_leader(sock, new_leader_addr):
    message = f'NEW_LEADER {new_leader_addr[0]} {new_leader_addr[1]}'
    for client in clients:
        sock.sendto(message.encode(), client)

if __name__ == "__main__":
    delay = 2

    # Determine se este relógio deve iniciar como líder
    role = input("Este relógio deve iniciar como líder? (s/n): ").strip().lower()
    is_leader = (role == 's')

    if is_leader:
        sync = False

    if not is_leader:
    # Defina o atraso desejado
      leader_ip = input("Digite o IP do líder inicial: ")
      leader_port = int(input("Digite a porta do líder inicial: "))
      leader_address = (leader_ip, leader_port)
      threading.Thread(target=sync_with_leader).start()

    threading.Thread(target=increment_time, args=(delay,)).start()
    threading.Thread(target=udp_server).start()
