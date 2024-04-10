import socket
import threading

def handle_client(clientsocket, address):
    '''
    Displays data received from the client.

    Parameters:
    clientsocket (socket.socket): The client socket object.
    address (tuple): The client address (host, port).
    '''
    while True:
        data = clientsocket.recv(1024).decode("utf-8")
        if not data:
            break
        print(f"{data}")

def start_server():
    '''
    Starts a TCP server by creating a socket connection.
    '''
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 5000))
    server_socket.listen(5)
    print('Server is now running...')

    while True:
        clientsocket, address = server_socket.accept()       
        client_thread = threading.Thread(target=handle_client, args=(clientsocket, address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
