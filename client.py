import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import datetime
import time

class ChatClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.withdraw()  # Hide the window initially
        
        # Get username
        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.window)
        if not self.username:
            self.username = "Anonymous"
        
        # Server configuration
        self.HOST = 'localhost'  # Change this to the server's IP address
        self.PORT = 5555
        
        # Animation variables
        self.typing_animation = None
        self.connection_animation = None
        self.last_message_time = time.time()
        
        # Create GUI
        self.setup_gui()
        
        # Connect to server
        self.connect_to_server()
        
        # Start receiving messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Show window and start main loop
        self.window.deiconify()
        self.window.mainloop()
    
    def setup_gui(self):
        """Setup the chat interface"""
        # Main window setup
        self.window.title(f"Chat Room - {self.username}")
        self.window.geometry("1000x700")
        self.window.configure(bg="#1E1E1E")
        self.window.minsize(800, 600)
        
        # Create main container
        main_container = tk.Frame(self.window, bg="#1E1E1E")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat area frame
        chat_frame = tk.Frame(main_container, bg="#2D2D2D", bd=2, relief=tk.GROOVE)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#2D2D2D",
            fg="#FFFFFF",
            font=("Segoe UI", 11),
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.chat_area.config(state=tk.DISABLED)
        
        # Message input area
        input_frame = tk.Frame(main_container, bg="#2D2D2D", bd=2, relief=tk.GROOVE)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Text input box with placeholder
        self.msg_entry = tk.Entry(
            input_frame,
            bg="#3D3D3D",
            fg="#CCCCCC",
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            borderwidth=0
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.msg_entry.bind("<Return>", self.send_message)
        self.msg_entry.bind("<Key>", self.on_typing)
        
        # Placeholder text
        self.msg_entry.insert(0, "Type your message here...")
        self.msg_entry.bind("<FocusIn>", self.on_entry_click)
        self.msg_entry.bind("<FocusOut>", self.on_focus_out)
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#007ACC",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=5,
            activebackground="#005999",
            activeforeground="white"
        )
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Status bar
        status_frame = tk.Frame(main_container, bg="#2D2D2D", height=20)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Connecting...",
            bg="#2D2D2D",
            fg="#FFA500",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Typing indicator
        self.typing_label = tk.Label(
            status_frame,
            text="",
            bg="#2D2D2D",
            fg="#888888",
            font=("Segoe UI", 9)
        )
        self.typing_label.pack(side=tk.RIGHT, padx=5)
        
        # Protocol for window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure styles
        self.configure_styles()
        
        # Start connection animation
        self.animate_connection()
    
    def configure_styles(self):
        """Configure custom styles for widgets"""
        style = ttk.Style()
        style.configure(
            "Custom.TButton",
            background="#007ACC",
            foreground="white",
            font=("Segoe UI", 11, "bold")
        )
    
    def animate_connection(self):
        """Animate the connection status"""
        dots = [".", "..", "..."]
        for i in range(3):
            self.status_label.config(text=f"Connecting{dots[i]}")
            self.window.update()
            time.sleep(0.3)
    
    def on_typing(self, event):
        """Handle typing animation"""
        if self.typing_animation:
            self.window.after_cancel(self.typing_animation)
        
        self.typing_label.config(text=f"{self.username} is typing...")
        
        # Clear typing indicator after 2 seconds of no typing
        self.typing_animation = self.window.after(2000, lambda: self.typing_label.config(text=""))
    
    def on_entry_click(self, event):
        """Function to clear placeholder text when entry is clicked"""
        if self.msg_entry.get() == "Type your message here...":
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.config(fg="white")
    
    def on_focus_out(self, event):
        """Function to restore placeholder text when entry loses focus"""
        if not self.msg_entry.get():
            self.msg_entry.insert(0, "Type your message here...")
            self.msg_entry.config(fg="#CCCCCC")
    
    def connect_to_server(self):
        """Connect to the chat server"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.HOST, self.PORT))
            self.add_message("Connected to the server!", "System")
            self.status_label.config(text="Connected", fg="#00FF00")
            
            # Animate successful connection
            self.window.after(100, lambda: self.status_label.config(fg="#00FF00"))
        except:
            messagebox.showerror("Error", "Could not connect to server!")
            self.window.destroy()
    
    def receive_messages(self):
        """Receive messages from the server"""
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    self.add_message(message)
            except:
                self.add_message("Lost connection to the server!", "System")
                self.status_label.config(text="Disconnected", fg="#FF0000")
                self.client.close()
                break
    
    def send_message(self, event=None):
        """Send message to the server"""
        message = self.msg_entry.get()
        if message and message != "Type your message here...":
            try:
                # Format message with username
                formatted_message = f"{self.username}: {message}"
                self.client.send(formatted_message.encode())
                self.msg_entry.delete(0, tk.END)
                # Restore placeholder
                self.msg_entry.insert(0, "Type your message here...")
                self.msg_entry.config(fg="#CCCCCC")
                
                # Clear typing indicator
                if self.typing_animation:
                    self.window.after_cancel(self.typing_animation)
                self.typing_label.config(text="")
                
                # Animate send button
                self.send_button.config(bg="#005999")
                self.window.after(100, lambda: self.send_button.config(bg="#007ACC"))
                
            except:
                self.add_message("Could not send message!", "System")
    
    def add_message(self, message, sender="Server"):
        """Add message to the chat area"""
        self.chat_area.config(state=tk.NORMAL)
        
        # Get current time
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        # Add timestamp and sender
        if sender == "System":
            self.chat_area.insert(tk.END, f"[{current_time}] ", "time")
            self.chat_area.insert(tk.END, f"{message}\n", "system")
        else:
            self.chat_area.insert(tk.END, f"[{current_time}] ", "time")
            self.chat_area.insert(tk.END, f"{message}\n")
        
        # Configure tags
        self.chat_area.tag_config("time", foreground="#888888")
        self.chat_area.tag_config("system", foreground="#FFA500")
        
        # Highlight new messages
        if time.time() - self.last_message_time > 1:  # If more than 1 second since last message
            self.chat_area.tag_add("highlight", "end-2c linestart", "end-1c")
            self.chat_area.tag_config("highlight", background="#3D3D3D")
            self.window.after(1000, lambda: self.chat_area.tag_remove("highlight", "1.0", "end"))
        
        self.last_message_time = time.time()
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                self.client.close()
            except:
                pass
            self.window.destroy()

if __name__ == "__main__":
    client = ChatClient() 