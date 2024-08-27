import socket
import ssl
import tkinter as tk
from tkinter import filedialog

class FileTransferGUI:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer")

        self.host_label = tk.Label(master, text="Host:")
        self.host_label.grid(row=0, column=0)

        self.host_entry = tk.Entry(master)
        self.host_entry.grid(row=0, column=1)

        self.port_label = tk.Label(master, text="Port:")
        self.port_label.grid(row=1, column=0)

        self.port_entry = tk.Entry(master)
        self.port_entry.grid(row=1, column=1)

        self.file_label = tk.Label(master, text="File:")
        self.file_label.grid(row=2, column=0)

        self.file_entry = tk.Entry(master)
        self.file_entry.grid(row=2, column=1)

        self.file_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.file_button.grid(row=2, column=2)

        self.transfer_button = tk.Button(master, text="Transfer", command=self.transfer_file)
        self.transfer_button.grid(row=3, column=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def transfer_file(self):
        HOST = self.host_entry.get()
        PORT = int(self.port_entry.get())
        FILE_PATH = self.file_entry.get()

        context = ssl._create_unverified_context()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            secure_s = context.wrap_socket(s, server_hostname=HOST)
            secure_s.connect((HOST, PORT))
            print(f'Connected to {HOST}:{PORT}')
            with open(FILE_PATH, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    secure_s.sendall(data)
            print('File transfer complete')

root = tk.Tk()
file_transfer_gui = FileTransferGUI(root)
root.mainloop()
