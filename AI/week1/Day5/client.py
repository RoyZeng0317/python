# client.py
import socket

# 1. create socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. connect to server of ip and port
print("Connecting to server...")
client_socket.connect(('127.0.0.1', 12345))

# 3. send the message for server(remember need deocde to bytes)
send_msg = "Hello Server, this is a client message."
client_socket.send(send_msg.encode('utf-8'))

# 4. recive the server answer
server_reply = client_socket.recv(1024).decode('utf-8')
print(f'recive server message: {server_reply}')

# 5. close the connection
client_socket.close()
print("Connection closed.")