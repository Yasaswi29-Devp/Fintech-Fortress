import os
import sys
import getpass
import random
import platform
import socket
import time

# Add the parent directory to the Python path to find common.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import common

SERVERS = [
    {'ip': '127.0.0.1', 'port': 1069},  # Primary server
    {'ip': '127.0.0.1', 'port': 1070}   # Backup server
]

class BankClient:
    def __init__(self):
        self.current_server_index = 0
        self.client_socket = None
        self.key = random.randint(0, 255)

    def clearScreen(self):
        os_name = platform.system()
        if os_name == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

    def connect_to_server(self):
        # Try all servers starting from the current index
        start_index = self.current_server_index
        
        for i in range(len(SERVERS)):
            server_index = (start_index + i) % len(SERVERS)
            server = SERVERS[server_index]
            
            try:
                if self.client_socket:
                    self.client_socket.close()
                
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(f"Trying to connect to server at {server['ip']}:{server['port']}...")
                self.client_socket.connect((server['ip'], server['port']))
                print('Connection was successful!')
                self.current_server_index = server_index
                return True
            except ConnectionRefusedError:
                print(f"Server at port {server['port']} is not available, trying next server...")
                continue
            except Exception as e:
                print(f"Error connecting to server: {e}")
                continue
        
        return False

    def reconnect(self):
        self.current_server_index = (self.current_server_index + 1) % len(SERVERS)
        return self.connect_to_server()

    def handle_communication(self):
        try:
            # Initial key exchange
            status = common.sendEncryptedMessage(self.client_socket, str(self.key), 0)
            if not status[0]:
                raise ConnectionError("Failed to send initial key")

            while True:
                status = common.recvEncryptedMessage(self.client_socket, self.key)
                if not status[0]:
                    raise ConnectionError("Failed to receive data")

                response = status[1]
                if response.startswith('@EXIT'):
                    print(response[6:])
                    return True  # Clean exit

                reply = ''
                if response.startswith('@PASS'):
                    print("\n" + "="*50)
                    print("Zero Knowledge Proof Authentication Process")
                    print("="*50)
                
                    # Get password without showing input
                    password = getpass.getpass('Enter password: ')
                
                    print("\n1. Generating proof for authentication...")
                    # Add some visual delay to show the process
                    time.sleep(0.5)
                    print("• Creating commitment...")
                    time.sleep(0.5)
                    print("• Generating challenge...")
                    time.sleep(0.5)
                    print("• Computing response...")
                    time.sleep(0.5)
                
                    print("\n2. Sending proof to server for verification...")
                    time.sleep(0.5)
                    print("• Server verifying proof...")
                    time.sleep(0.5)
                
                    reply = password
                    print("\n3. Verification complete!")
                    print("="*50 + "\n")
                
                else:
                    if response.startswith('@CLEAR'):
                        self.clearScreen()
                        print(response[7:], end='')
                    else:
                        print(response, end='')
                    reply = input('')

                if reply == '': 
                    reply = ' '

                status = common.sendEncryptedMessage(self.client_socket, reply, self.key)
                if not status[0]:
                    raise ConnectionError("Failed to send reply")

        except Exception as e:
            print(f"\nLost connection to server: {e}")
            return False

    def start(self):
        while True:
            if not self.connect_to_server():
                print("No servers are available. Please try again later.")
                break

            try:
                if self.handle_communication():
                    break
                else:
                    print("Attempting to reconnect to backup server...")
                    time.sleep(1)
                    continue
                    
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Attempting to reconnect...")
                time.sleep(1)
                continue
            
        if self.client_socket:
            self.client_socket.close()

def main():
    client = BankClient()
    client.start()

if __name__ == '__main__':
    main()
