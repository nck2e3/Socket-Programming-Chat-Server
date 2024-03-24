import socket
import threading
from datetime import datetime
import csv  # Import the CSV module for writing CSV files

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5
active_clients = []

# Set to store previously sent messages
sent_messages = set()

def listen_for_messages(client, username):
    while True:
        try:
            message = client.recv(2048).decode('utf-8')
            if message:
                final_msg = username + '~' + message
                send_messages_to_all(final_msg)
            else:
                print(f"The message sent from client {username} is empty")
                break  # Client disconnected
        except ConnectionResetError:
            print(f"Client {username} disconnected")
            active_clients.remove((username, client))
            send_messages_to_all(f"{username} left the chatroom")  # Notify all clients
            break

def send_message_to_client(client, message):
    client.sendall(message.encode())

def send_messages_to_all(message):
    if message not in sent_messages:
        for user in active_clients:
            send_message_to_client(user[1], message)
        sent_messages.add(message)
        # Save the message with timestamp to a CSV file
        with open("chat_record.csv", "a", newline='') as file:  # Open the CSV file in append mode
            writer = csv.writer(file)
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message])

def client_handler(client):
    while True:
        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
            prompt_message = "SERVER~" + f"{username} added to the chat"
            send_messages_to_all(prompt_message)
            break
        else:
            print("Client username is empty")
    threading.Thread(target=listen_for_messages, args=(client, username, )).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")
    server.listen(LISTENER_LIMIT)
    while True:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")
        threading.Thread(target=client_handler, args=(client,)).start()

if __name__ == '__main__':
    main()
