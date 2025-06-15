import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import json
import sys

# Server configuration
HOST = '0.0.0.0'
PORT = 5555

# List to store all connected clients
clients = []

class ChatServer:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen()
        
        self.rooms = {}  # Dictionary to store room information
        self.clients = {}  # Dictionary to store client information
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title(f"Chat Server - {self.host}:{self.port}")
        self.root.geometry("600x400")
        
        # Create text area for server logs
        self.log_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=20)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.log(f"Server started on {self.host}:{self.port}")
        
        # Start accepting connections in a separate thread
        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.daemon = True
        self.accept_thread.start()
        
        self.root.mainloop()
    
    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
    
    def accept_connections(self):
        while True:
            client_socket, address = self.server.accept()
            self.log(f"New connection from {address}")
            
            # Start a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
    
    def handle_client(self, client_socket, address):
        try:
            # Add client to the list
            clients.append(client_socket)
            self.log(f"New connection from {address}")
            
            # Send welcome message
            welcome_msg = f"Welcome to the chat room! Connected from {address}"
            client_socket.send(welcome_msg.encode())
            
            # Broadcast new user joined
            join_msg = f"User from {address} joined the chat"
            self.broadcast(join_msg.encode())
            
            # Handle messages from this client
            while True:
                try:
                    message = client_socket.recv(1024)
                    if not message:
                        break
                        
                    # Broadcast message to all other clients
                    self.broadcast(message, client_socket)
                    
                except:
                    break
                    
        except:
            self.log(f"Connection with {address} closed")
        finally:
            # Remove client from list and close connection
            if client_socket in clients:
                clients.remove(client_socket)
            client_socket.close()
            # Broadcast user left message
            leave_msg = f"User from {address} left the chat"
            self.broadcast(leave_msg.encode())
    
    def broadcast(self, message, sender=None):
        """Send message to all connected clients except the sender"""
        for client in clients:
            if client != sender:
                try:
                    client.send(message)
                except:
                    clients.remove(client)

def broadcast(message, sender=None):
    """Send message to all connected clients except the sender"""
    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client_socket, address):
    """Handle individual client connections"""
    try:
        # Add client to the list
        clients.append(client_socket)
        print(f"New connection from {address}")
        
        # Send welcome message
        welcome_msg = f"Welcome to the chat room! Connected from {address}"
        client_socket.send(welcome_msg.encode())
        
        # Broadcast new user joined
        join_msg = f"User from {address} joined the chat"
        broadcast(join_msg.encode())
        
        while True:
            # Receive message from client
            message = client_socket.recv(1024)
            if not message:
                break
                
            # Broadcast message to all other clients
            broadcast(message, client_socket)
            
    except:
        print(f"Connection with {address} closed")
    finally:
        # Remove client from list and close connection
        if client_socket in clients:
            clients.remove(client_socket)
        client_socket.close()
        # Broadcast user left message
        leave_msg = f"User from {address} left the chat"
        broadcast(leave_msg.encode())

def start_server():
    """Start the chat server"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Add socket reuse option
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        
        print(f"Server started on {HOST}:{PORT}")
        print("Waiting for connections...")
        print("Press Ctrl+C to stop the server")
        
        while True:
            client_socket, address = server.accept()
            # Create new thread for each client
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.daemon = True  # Make thread daemon so it exits when main program exits
            thread.start()
            
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Please try the following:")
            print("1. Check if another instance of the server is running")
            print("2. Wait a few minutes and try again")
            print("3. Use a different port by changing the PORT variable")
            sys.exit(1)
        else:
            print(f"Error: {e}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server.close()
        sys.exit(0)

if __name__ == "__main__":
    start_server() 