import socket
import pickle

# Define the server addresses and ports for the three KV stores
server_addresses = [
    ("127.0.0.1", 8888),
    ("127.0.0.1", 8889),
    ("127.0.0.1", 8890)
]

# Define the test commands (you can add more if needed)
commands = [
    {"action": "put", "key": "ironman", "value": "Tony Stark"},
    {"action": "put", "key": "spiderman", "value": "Peter Parker"},
    {"action": "get", "key": "ironman"},
    {"action": "get", "key": "spiderman"},
    {"action": "delete", "key": "spiderman"},
    {"action": "get", "key": "spiderman"},
    {"action": "exit"}
]

try:
    # Create a socket for each KV store and connect to them
    client_sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(len(server_addresses))]
    for i, server_address in enumerate(server_addresses):
        client_sockets[i].connect(server_address)
        print(f"Connected to KV Store {i+1}")

    for command in commands:
        for i, client_socket in enumerate(client_sockets):
            # Serialize the command using pickle
            command_data = pickle.dumps(command)

            # Send the command to the KV store
            client_socket.send(command_data)

            # Receive and deserialize the response
            response_data = client_socket.recv(1024)
            response = pickle.loads(response_data)

            # Display the response along with the KV store identifier
            print(f"KV Store {i+1} - Command: {command}, Response: {response}")

except Exception as e:
    print("Error:", e)
finally:
    # Close all the client sockets
    for client_socket in client_sockets:
        client_socket.close()
