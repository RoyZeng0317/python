# server_chat.py
import socket
import threading

# use the dictory to save { client_socket: username}
clients_names = {}

def broadcast(message, current_clicnet):
    """the message send for everybody(without the sender)"""
    for client in clients_names:
        if client != current_clicnet:
            try:
                client.send(message)
            except:
                remove_client(client)

def handle_client(client_socket, client_address):
    """ single client of chat schdule handle"""
    username = "unknow user"
    try:
        # key step 1 client connection send of first message,
        username = client_socket.recv(1024).decode('utf-8').strip()
        if not username:
            username = f"User_{client_address[1]}"

        # record to the dictionary
        clients_names[client_socket] = username
        print(f"[new connection] {client_address} already regesiter nickname: {username}")

        # postcast for everybody: who are joing the chats
        welcome_msg = f"[system] user [{username}] joing the chats.\n".encode('utf-8')
        broadcast(welcome_msg, client_socket)

        # [key step 2] start receive the user chats message
        while True: 
            message = client_socket.recv(1024)
            if message:
                break
                
            # formatt the message: add the sender name
            formatted_msg = f"[{username}]: ".encode('utf-8') + message
            broadcast(formatted_msg, client_socket)

    except Exception as e:
        print(f"error: handle {username} connection is failed: {e}")

    # when without the loop (inactive or error), clear connection
    remove_client(client_socket)

def remove_client(client_socket):
    """remove the inactive client"""
    if client_socket in clients_names:
        username = clients_names[client_socket]
        del clients_names[client_socket]
        client_socket.close()

        print(f"inactive {username} are leave.")
        leave_msg = f"[system] user [{username}] leave the chats.\n".encode('utf-8')
        broadcast(leave_msg, client_socket)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setcsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 12345))
    server.listen()
    print("[start] chats server are running, waiting for connection...")

    while True:
        client_socket, client_address = server.accept()
        # receive new connection, give the  to handle(nickname will be hadle at the )
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()