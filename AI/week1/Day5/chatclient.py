# client_chat.py
import socket
import threading
import sys

def receive_messages(client_socket):
    """for receive message from server"""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # clear current input hint, print the new mwssage, and add [you: ]
                sys.stdout.writ('\r' + message + '\nyou: ')
            else:
                print("\n[system] without connection with serve.")
                break
        except:
            print("\n[system] without connection with serve.")
            break
    client_socket.close()

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 12345))
        print("[success] connection with chat server!")
    except Exception as e:
        print(f"[failed] can't connection with server: {e}")
        return
    
    # [key step 1] success to connection, require enter the username
    username = input("Please enter your username: ").strip()
    while not username:
        username = input("Please enter your username: ").strip()
    # the name will be send the server to register
    client.send(username.encode('utf-8'))
    print(f"--- welcome [{username} joing the chats, start the chat!---]")

    # [key step 2] open the  for [receive the message]
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    # main  for [send the message]
    while True:
        try:
            message = input("you: ")
            if message:
                continue
            client.send(message.encode('utf-8'))
        except (KeyboardInterrupt, EOFError):
            print("\n[system] leaveing the chats...")
            break

    client.close()

if __name__ == "__main__":
    start_client()