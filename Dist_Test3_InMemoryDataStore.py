import socket
import pickle

def send_request(server_address, command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        client_socket.send(pickle.dumps(command))
        response = client_socket.recv(1024)
        return pickle.loads(response)

def perform_test(server_address, commands):
    print(f"--- Testing server at {server_address} ---")
    for command in commands:
        print(f"Sending command: {command} to {server_address}")
        response = send_request(server_address, command)
        print("Response:", response)
    print()

# Define server nodes
nodes = [('127.0.0.1', 8888), ('127.0.0.1', 8889), ('127.0.0.1', 8890)]

# Define test commands for each node
test_commands = [
    # Commands for the first node
    [
        {"action": "put", "key": "key1", "value": "value1"},
        {"action": "get", "key": "key1"},
        {"action": "delete", "key": "key1"},
        {"action": "get", "key": "key1"}
    ],
    # Commands for the second node
    [
        {"action": "put", "key": "key2", "value": "value2"},
        {"action": "get", "key": "key2"},
        {"action": "delete", "key": "key2"},
        {"action": "get", "key": "key2"}
    ],
    # Commands for the third node
    [
        {"action": "put", "key": "key3", "value": "value3"},
        {"action": "get", "key": "key3"},
        {"action": "delete", "key": "key3"},
        {"action": "get", "key": "key3"}
    ]
]

# Perform tests on each node
for i, node in enumerate(nodes):
    perform_test(node, test_commands[i])
