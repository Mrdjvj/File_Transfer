import os
import socket
import ssl
import threading

class Server:
    def __init__(self,hostname,transfer_port,ping_port,cert,key):
        self.hostname = hostname
        self.transfer_port = transfer_port
        self.ping_port = ping_port
        self.cert = cert
        self.key = key
        
        self.active_users = {}

        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_ping_socket = ssl.wrap_socket(self.ping_socket, certfile=self.cert, keyfile=self.key,server_side = True)
        self.secure_ping_socket.bind((self.hostname,self.ping_port))
        self.secure_ping_socket.listen()

        self.transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_transfer_socket = ssl.wrap_socket(self.transfer_socket, certfile=self.cert, keyfile=self.key, server_side=True)
        self.secure_transfer_socket.bind((self.hostname, self.transfer_port))
        self.secure_transfer_socket.listen()

    def handle_new_connection(self, client_connection):
        client_socket = client_connection[0]
        ping_type = client_socket.recv(256).decode()
        username = client_socket.recv(4096).decode()
        if ping_type == "INIT":
            client_address = client_connection[1]
            print(f"{username} is connected from {client_address}!")
            # Getting IP address from the connected client
            self.active_users[username] = client_socket.getpeername()[0]
        elif ping_type == "END":
            self.active_users.pop(username)
            print(f"{username} has ended the connection!")
    
    def file_transfer(self,client_connection):
        sender_side_socket = client_connection[0]
        sender_address = client_connection[1]

        username = sender_side_socket.recv(4096).decode()
        file_name = sender_side_socket.recv(4096).decode()
        recipient = sender_side_socket.recv(4096).decode()
        file_contents = sender_side_socket.recv(4096)

        recipient_IP = self.active_users.get(recipient)
        if not recipient_IP:
            print(f"{recipient} Not Found!")
            sender_side_socket.send(0).encode()
            return
        recipient_side_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        secure_recipient_side_socket = ssl.wrap_socket(recipient_side_socket, certfile=self.cert, keyfile=self.key)
        secure_recipient_side_socket.bind((self.hostname, self.transfer_port+2))
        secure_recipient_side_socket.connect((recipient_IP, 11000))

        secure_recipient_side_socket.send(username.encode())
        secure_recipient_side_socket.send(file_name.encode())
        secure_recipient_side_socket.send(file_contents)

        acknowledgement = secure_recipient_side_socket.recv(1).decode()
        if acknowledgement:
            print(f"{file_name} was sent successfully to {recipient} from {username}")
        
        



file_transfer_server = Server("10.30.203.76",9000,10000,"host.cert","host.key")

def connections_thread_runner(file_transfer_server):
    while True:
        client_ping_socket, client_address = file_transfer_server.secure_ping_socket.accept()
        client_connection = (client_ping_socket, client_address)
        new_connections_thread = threading.Thread(target=file_transfer_server.handle_new_connection, args=[client_connection])
        new_connections_thread.start()

def transfer_thread_runner(file_transfer_server):
    while True:
        sender_side_transfer_socket, sender_address = file_transfer_server.secure_transfer_socket.accept()
        client_connection = (sender_side_transfer_socket, sender_address)
        file_transfer_thread = threading.Thread(target=file_transfer_server.file_transfer, args=[client_connection])
        file_transfer_thread.start()

#while True:
new_connections_thread = threading.Thread(target=connections_thread_runner, args=[file_transfer_server])
new_connections_thread.start()

file_transfer_thread = threading.Thread(target=transfer_thread_runner, args=[file_transfer_server])
file_transfer_thread.start()

thread_list=[new_connections_thread,file_transfer_thread]
for thread in thread_list:
    thread.join()

