# TCP Chat Application

A simple TCP-based chat application that allows users to connect to chat rooms using an 11-digit room code. The application features automatic IP and port detection.

## Features

- Automatic IP and port detection
- Room-based chat system with 11-digit room codes
- Graphical user interface for both server and client
- Real-time message broadcasting
- User join/leave notifications

## Requirements

- Python 3.x
- Required packages (install using `pip install -r requirements.txt`):
  - socket
  - tkinter
  - threading

## How to Use

1. First, start the server:
   ```bash
   python server.py
   ```
   The server will automatically detect the IP address and assign a free port.

2. Start the client application:
   ```bash
   python client.py
   ```

3. In the client application:
   - Enter your desired username
   - Enter an 11-digit room code (you can make up any 11 digits)
   - Click "Connect" to join the chat room

4. To chat with others:
   - Share the room code with other users
   - They need to enter the same room code to join your chat room
   - Type messages in the input field and press Enter or click "Send"

## Notes

- The server must be running for clients to connect
- Multiple clients can join the same room using the same room code
- Messages are only visible to users in the same room
- The server window shows connection logs and room activity 