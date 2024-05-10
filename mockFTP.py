import socket
import datetime

# Define the maximum login attempts
MAX_LOGIN_ATTEMPTS = 3

# Create a dictionary to store login attempts
login_attempts = {}

def handle_login(client_socket, address):
    attempts = login_attempts.get(address[0], 0)
    if attempts >= MAX_LOGIN_ATTEMPTS:
        client_socket.send(b"Too many login attempts. Connection terminated.\n")
        return False

    client_socket.send(b"220 Welcome to the mock FTP server\n")
    client_socket.send(b"331 Please specify the password\n")
    password_attempt = client_socket.recv(1024).strip().decode('utf-8')
    # Log the login attempt
    with open("login_attempts.log", "a") as f:
        f.write(f"Timestamp: {datetime.datetime.now()}, Username: anonymous, Password: {password_attempt}, Source IP: {address[0]}, TTL: {address[1]}\n")
    login_attempts[address[0]] = attempts + 1
    if password_attempt == "password":
        client_socket.send(b"230 Login successful\n")
        return True
    else:
        client_socket.send(b"530 Login incorrect\n")
        return False

def handle_connection(client_socket, address):
    client_socket.send(b"220 Welcome to the mock FTP server\n")
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        command = data.strip().decode('utf-8')
        if command.upper() == "USER":
            if handle_login(client_socket, address):
                break
        elif command.upper() == "QUIT":
            break
        else:
            client_socket.send(b"530 Please login with USER command\n")
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 21))
    server_socket.listen(5)
    print("Mock FTP server started on port 21...")
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address[0]}:{address[1]}")
            handle_connection(client_socket, address)
    except KeyboardInterrupt:
        print("Server terminated.")

if __name__ == "__main__":
    main()
