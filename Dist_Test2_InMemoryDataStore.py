import socket
import pickle

def send_request(server_address, command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        client_socket.send(pickle.dumps(command))
        response = client_socket.recv(1024)
        return pickle.loads(response)

# Define nodes and test commands
nodes = [('127.0.0.1', 8890), ('127.0.0.1', 8889)]
commands = [
    {"action": "put", "key": "forward_test_key2", "value": "Value2"},  # Intended for Node 1
    {"action": "get", "key": "forward_test_key2"}  # Intended for Node 2
]

# Send command 1 to node 1 and command 2 to node 2
for i, command in enumerate(commands):
    test_server_address = nodes[i % len(nodes)]
    print(f"Sending command to {test_server_address}: {command}")
    response = send_request(test_server_address, command)
    print("Response:", response)
