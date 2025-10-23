import socket
import threading
from datetime import datetime

# Basic server settings
TCP_PORT = 13000
BUFFER = 1024
tcp_clients = {}

def timestamp():
    return datetime.now().strftime("[%H:%M:%S]")

def format_msg(sender, target, msg, private=False):
    tag = "[PRIVATE]" if private else ""
    return f"{timestamp()} {tag} [{sender} → {target}] {msg}".strip()

def broadcast_tcp(msg, sender=None):
    # Send message to all connected users except sender
    print(msg)
    for user, conn in list(tcp_clients.items()):
        if user != sender and conn:
            try:
                conn.sendall((msg + "\n").encode())
            except:
                tcp_clients.pop(user, None)

def private_msg_tcp(sender, target, msg):
    # Send private message between two users
    m = format_msg(sender, target, msg, private=True)
    if target in tcp_clients and tcp_clients[target]:
        try:
            tcp_clients[target].sendall((m + "\n").encode())
            if sender in tcp_clients and tcp_clients[sender]:
                tcp_clients[sender].sendall((m + "\n").encode())
        except:
            tcp_clients[sender].sendall(f"[System] Failed to send to {target}\n".encode())
    else:
        tcp_clients[sender].sendall(f"[System] User '{target}' not found.\n".encode())

def test_message_tcp(sender, target):
    private_msg_tcp(sender, target, "🔔 Test OK")

def handle_tcp_client(conn, addr):
    # Handle a single connected client
    conn.sendall(b"Enter your username: ")
    username = conn.recv(BUFFER).decode().strip()
    if not username:
        conn.sendall(b"[System] Invalid username.\n")
        conn.close()
        return

    tcp_clients[username] = conn
    broadcast_tcp(format_msg("System", "All", f"{username} joined the chat."))
    conn.sendall(b"\nCommands:\n"
                 b"  /who          - List online users\n"
                 b"  /test name    - Send test message\n"
                 b"  @name msg     - Private message\n"
                 b"  exit          - Leave chat\n\n")

    while True:
        try:
            data = conn.recv(BUFFER)
            if not data:
                break
            msg = data.decode().strip()
            if not msg:
                conn.sendall(b"[System] Cannot send blank message.\n")
                continue

            # Command handling
            if msg.lower() == "exit":
                break
            elif msg == "/who":
                users = ", ".join(tcp_clients.keys())
                conn.sendall(f"[System] Online: {users}\n".encode())
            elif msg.startswith("/test "):
                _, target = msg.split(" ", 1)
                test_message_tcp(username, target)
            elif msg.startswith("@"):
                parts = msg.split(" ", 1)
                if len(parts) == 2:
                    private_msg_tcp(username, parts[0][1:], parts[1])
                else:
                    conn.sendall(b"[System] Usage: @username message\n")
            else:
                broadcast_tcp(format_msg(username, "All", msg), username)
        except Exception as e:
            print(f"[Error] {username}: {e}")
            break

    conn.close()
    tcp_clients.pop(username, None)
    broadcast_tcp(format_msg("System", "All", f"{username} left the chat."))

def server_chat_input(name, server_socket):
    # Server can also send messages to clients
    while True:
        msg = input().strip()
        if not msg:
            print("[System] Cannot send blank message.")
            continue
        if msg.lower() == "exit":
            print("🚪 Server shutting down...")
            for conn in list(tcp_clients.values()):
                if conn:
                    conn.close()
            server_socket.close()
            tcp_clients.clear()
            return
        elif msg.startswith("@"):
            parts = msg.split(" ", 1)
            if len(parts) == 2:
                private_msg_tcp(name, parts[0][1:], parts[1])
            else:
                print("[System] Usage: @username message")
        else:
            broadcast_tcp(format_msg(name, "All", msg), name)

def run_tcp_server():
    # Start the TCP chat server
    name = input("Enter server name: ").strip() or "Server"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", TCP_PORT))
    s.listen(5)
    tcp_clients[name] = None
    print(f"{timestamp()} [{name}] TCP server running on port {TCP_PORT}")
    threading.Thread(target=server_chat_input, args=(name, s), daemon=True).start()

    try:
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
    except OSError:
        pass

def tcp_client(ip):
    # Connect as TCP client
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        c.connect((ip, TCP_PORT))
        print(f"[System] Connected to {ip}:{TCP_PORT}")
    except:
        print("[System] Cannot connect to server.")
        return

    threading.Thread(target=recv_tcp, args=(c,), daemon=True).start()

    while True:
        msg = input().strip()
        if not msg:
            print("[System] Cannot send blank message.")
            continue
        c.sendall(msg.encode())
        if msg.lower() == "exit":
            print("[System] Disconnecting...")
            c.close()
            break

def recv_tcp(sock):
    # Listen for incoming messages from server
    while True:
        try:
            data = sock.recv(BUFFER)
            if not data:
                print("\n[System] Disconnected from server.")
                break
            print("\n" + data.decode().strip())
        except:
            break
