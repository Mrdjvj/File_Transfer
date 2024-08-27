# Importing the required modules
import socket
import ssl

# Specifying the server-side IP Address and port number
HOST = '10.5.25.19'
PORT = 12345

# Creating an SSL verified context, using SSL certificate and key files
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="host.cert", keyfile="host.key")

# Creating the socket and binding with the server-side IP address and port number
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Server is listening...')
    while True:
        # Creating the acceptor objects
        conn, addr = s.accept()
        print(f'Connected by {addr}')
        with conn:
            # Creating the file to receive the contents
            with open('received_file.txt', 'wb') as f:
                # Wrapping the socket with the SSL context
                with context.wrap_socket(conn, server_side=True) as secure_conn:
                    while True:
                        # Receiving the contents
                        data = secure_conn.recv(1024)
                        if not data:
                            break
                        # Writing the data to the receiving file
                        f.write(data)
        print('File transfer complete')
