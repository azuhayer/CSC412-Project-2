import socket
import datetime

MAX_LOGIN_ATTEMPTS = 3
PORT_SCAN_THRESHOLD = 3

class MockFTPServer:
    def __init__(self):
        self.log_file = open("ftp_server_log.txt", "a")
        self.login_attempts = {}
        self.port_scan_attempts = {}

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(f"[{timestamp}] {message}\n")
        print(message)

    def handle_connection(self, client_socket, address):
        self.log(f"Connection from {address[0]}:{address[1]}")
        try:
            client_socket.sendall(b"220 Welcome to Mock FTP Server\r\n")
            login_attempt_count = 0
            while login_attempt_count < MAX_LOGIN_ATTEMPTS:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                if "USER" in data.upper():
                    username = data.split(" ")[1]
                    self.log(f"Login attempt with username '{username}' from {address[0]}")
                    if address[0] in self.login_attempts:
                        self.login_attempts[address[0]] += 1
                    else:
                        self.login_attempts[address[0]] = 1

                    if self.login_attempts[address[0]] > MAX_LOGIN_ATTEMPTS:
                        self.log(f"Max login attempts reached. Terminating connection from {address[0]}")
                        client_socket.sendall(b"530 Maximum login attempts reached. Disconnecting...\r\n")
                        break
                    else:
                        client_socket.sendall(b"331 Password required for user.\r\n")
                        password_attempt = client_socket.recv(1024).decode().strip()
                        password = password_attempt.split(" ")[1]
                        if username == "dummyuser" and password == "dummypassword":
                            client_socket.sendall(b"230 Login successful.\r\n")
                            self.log(f"Login successful for username '{username}' from {address[0]}")
                            while True:
                                data = client_socket.recv(1024).decode().strip()
                                # Implement FTP command handling here
                                if data.upper() == "QUIT":
                                    self.log(f"Client {address[0]}:{address[1]} disconnected.")
                                    break
                                else:
                                    self.log(f"Received FTP command '{data}' from {address[0]}")
                                    client_socket.sendall(b"200 Command okay.\r\n")
                            break
                        else:
                            client_socket.sendall(b"530 Login incorrect. Please try again.\r\n")
                            self.log(f"Login attempt failed for username '{username}' from {address[0]}")
                            login_attempt_count += 1
                else:
                    client_socket.sendall(b"530 Please login with USER command.\r\n")
        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            client_socket.close()

    def detect_port_scan(self, address):
        if address[0] in self.port_scan_attempts:
            self.port_scan_attempts[address[0]] += 1
        else:
            self.port_scan_attempts[address[0]] = 1

        if self.port_scan_attempts[address[0]] >= PORT_SCAN_THRESHOLD:
            self.log(f"Port scan detected from {address[0]}")
            # Take appropriate action, like blocking IP or logging to a separate file

    def start(self, host='', port=21):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen(5)
            self.log(f"Mock FTP server started on port {port}")

            while True:
                client_socket, address = server_socket.accept()
                self.detect_port_scan(address)
                self.handle_connection(client_socket, address)

if __name__ == "__main__":
    ftp_server = MockFTPServer()
    ftp_server.start()
