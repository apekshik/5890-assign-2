import socket
import pickle  # We'll use pickle for serialization/deserialization

# Define the server address and port
server_address = ("127.0.0.1", 8888)

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

commands2 = [ 
    {"action": "get", "key": "ironman"},
    {"action": "get", "key": "spiderman"},
    {"action": "exit"}
]

# Create a socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

print("connected to server")

try:
    for command in commands:
        # Serialize the command using pickle
        print("Command: ", command)
        command_data = pickle.dumps(command)
        # print("command_data:", command_data)
        # Send the command to the server
        client_socket.send(command_data)
        print("sent")
        # Receive and deserialize the response
        response_data = client_socket.recv(1024)
        response = pickle.loads(response_data)

        # Display the response
        print("Response:", response)
except Exception as e:
    print("Error:", e)
finally:
    # Close the socket
    client_socket.close()
