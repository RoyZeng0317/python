# server.py
import socket

# 1. create socket object

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. bind ip and port
server_socket.bind(('127.0.0.1', 12345))

# 3. listen
server_socket.listen(1)
print("Server are start, waiting for client connection...")

# 4. receive client connection (program will be stopped at here, until connection with people)
client_socket, client_address = server_socket.accept()
print(head_msg:= f"success connection with {client_address}!")

# 5. recive the client send meessage(maxium is recive 1024 bytes)
# Network send must bytes, so needs to use utf-8 encoing to string at receive.
data = client_socket.recv(1024).decode('utf-8')
print(f'recive client message: {data}')

# 6. reply message for client (must encode to bytes)
response_msg = "Hello Client! I get your message."
client_socket.send(response_msg.encode('utf-8'))

# 7. close the connection
client_socket.close()
server_socket.close()
print("Connection closed.")