import os
import socket
import ssl
import threading
import tkinter as tk
from tkinter import filedialog

class FileTransferGUI:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer")

        self.username_label = tk.Label(master, text="Username:")
        self.username_label.grid(row=0,column=0)

        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=0,column=1)

        self.initiate_activity_button = tk.Button(master, text="Initiate Activity", command=self.initiate_activity)
        self.initiate_activity_button.grid(row=0,column=2)

        self.file_label = tk.Label(master, text="File:")
        self.file_label.grid(row=1,column=0)

        self.file_entry = tk.Entry(master)
        self.file_entry.grid(row=1,column=1)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=1,column=2)

        self.recipient_label = tk.Label(master, text="Recipient")
        self.recipient_label.grid(row=2,column=0)

        self.recipient_entry = tk.Entry(master)
        self.recipient_entry.grid(row=2,column=1)

        self.transfer_button = tk.Button(master, text="Transfer", command=self.send_file)
        self.transfer_button.grid(row=3,column=1)

        self.exit_button = tk.Button(master, text="Exit", command=self.end_activity)
        self.exit_button.grid(row=3,column=2)

        self.server_hostname = '10.30.203.76'
        self.server_transfer_port = 9000
        self.client_transfer_port = 9001
        self.server_ping_port = 10000
        self.client_hostname = "10.30.203.76"
        self.client_recipient_port = 11000

        self.server_ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ping_socket_context = ssl._create_unverified_context()
        self.secure_server_ping_socket = self.server_ping_socket_context.wrap_socket(self.server_ping_socket,server_hostname=self.server_hostname)
        self.secure_server_ping_socket.connect((self.server_hostname,self.server_ping_port))
    
        self.file_transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_transfer_socket_context = ssl._create_unverified_context()
        self.secure_file_transfer_socket = self.file_transfer_socket_context.wrap_socket(self.file_transfer_socket, server_hostname=self.server_hostname)
        self.secure_file_transfer_socket.bind((self.client_hostname,self.client_transfer_port))
        self.secure_file_transfer_socket.connect((self.server_hostname,self.server_transfer_port))

        self.file_recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_recipient_socket_context = ssl._create_unverified_context()
        self.secure_file_recipient_socket = self.file_recipient_socket_context.wrap_socket(self.file_recipient_socket, server_hostname=self.server_hostname)
        self.secure_file_recipient_socket.bind((self.client_hostname, self.client_recipient_port))
        #self.secure_file_recipient_socket.connect((self.server_hostname, self.server_transfer_port))
        self.secure_file_recipient_socket.listen()
    def initiate_activity(self):
        username = self.username_entry.get()
        print(f"{username} is the name to be used by this client")
        self.secure_server_ping_socket.send("INIT".encode())
        self.secure_server_ping_socket.send(username.encode())
    
    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)
    
    def send_file(self):
        username = self.username_entry.get()
        file_path = self.file_entry.get()
        file_name = os.path.basename(file_path)
        recipient = self.recipient_entry.get()

        with open(file_path, 'rb') as file_reader:
            file_contents = file_reader.read()

        self.secure_file_transfer_socket.send(username.encode())
        self.secure_file_transfer_socket.send(file_name.encode())
        self.secure_file_transfer_socket.send(recipient.encode())
        self.secure_file_transfer_socket.send(file_contents)

        acknowledgement = self.secure_file_transfer_socket.recv(1).decode()
        if acknowledgement:
            print(f"{file_name} sent to {recipient}")
        self.secure_file_transfer_socket.close()

    def receive_file(self, server_connection):
        server_side_socket = server_connection[0]
        server_address = server_connection[1]
        
        sender = server_side_socket.recv(4096).decode()
        file_name = server_side_socket.recv(4096).decode()
        file_contents = server_side_socket.recv(4096)

        with open(file_name, 'wb') as file_writer:
            file_writer.write(file_contents)
        
        server_side_socket.send('1'.encode())

    def end_activity(self):
        username = self.username_entry.get()
        print(f"{username} has ended the connection")
        self.secure_server_ping_socket.send("END".encode())
        self.secure_server_ping_socket.send(username.encode())
       
        self.secure_file_recipient_socket.close()
        self.file_recipient_socket.close()

        self.secure_file_transfer_socket.close()
        self.file_transfer_socket.close()

        self.secure_server_ping_socket.close()
        self.server_ping_socket.close()

        exit()

def file_recipient_runner(file_transfer_client):
    while True:
        server_side_socket, server_address = file_transfer_client.secure_file_recipient_socket.accept()
        server_connection = (server_side_socket,server_address)
        file_recipient_thread = threading.Thread(target=file_transfer_client.receive_file, args=(server_connection))
        file_recipient_thread.start()

root = tk.Tk()
file_transfer_client = FileTransferGUI(root)
root.mainloop()
while True:
    file_recipient_runner(file_transfer_client)
