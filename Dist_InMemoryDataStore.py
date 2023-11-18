import socket
# We use pickle for serialization/deserialization
import pickle
import threading  
import time
import sys

import hashlib

class SimpleConsistentHashing:
    def __init__(self, nodes=None):
        self.nodes = sorted(nodes) if nodes else []

    def get_node(self, key):
        if not self.nodes:
            return None
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        node_index = hash_val % len(self.nodes)
        return self.nodes[node_index]

# Assuming three different ports for three KV store instances
nodes = ['127.0.0.1:8888', '127.0.0.1:8889', '127.0.0.1:8890']
ring = SimpleConsistentHashing(nodes)

# Define the maximum number of concurrent clients to handle
MAX_CONCURRENT_CLIENTS = 5
client_handler_semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_CLIENTS)

class InMemoryKeyValueStore:
    def __init__(self, port, filename_template="key_value_store_{}.pkl"):
        # Filename now includes the port number
        self.filename = filename_template.format(port)
        self.store = self.load_from_disk()


    def put(self, key, value):
        self.store[key] = value
        return "Put successful"  # Return a success message


    def get(self, key):
        if key in self.store:
            return self.store[key]  # Return the value if the key exists
        else:
            return "Key not found"  # Return an error message


    def delete(self, key):
        if key in self.store:
            del self.store[key]
            return "Delete successful"  # Return a success message
        else:
            return "Key not found"  # Return an error message


    def save_to_disk(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.store, file)


    def load_from_disk(self):
        try:
            with open(self.filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}  # Handle the case where the file doesn't exist yet

    
    def auto_save_thread(self, interval_seconds=5):
        while True:
            time.sleep(interval_seconds)
            self.save_to_disk()
            # print("Key-value store saved to disk.")

    # New method to send request to the correct node
    def send_request_to_node(self, node_address, request_data):
        node_ip, node_port = node_address.split(':')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.connect((node_ip, int(node_port)))
            node_socket.send(pickle.dumps(request_data))
            response = node_socket.recv(1024)
            return pickle.loads(response)

    def __str__(self):
        # Get the first three key-value pairs (items) from the dictionary
        first_three_items = list(self.store.items())[:3]

        if len(self.store) <= 3:
            # If there are 3 or fewer items, print the whole store
            return str(self.store)
        else:
            # If there are more than 3 items, print only the first three
            return str(dict(first_three_items))

# Create server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # Modify the server address and port to be dynamic
# server_port = 8888  # This should be changed based on the instance
# server_address = ("127.0.0.1", server_port)

# Parse the command-line argument for the server port
if len(sys.argv) != 2:
    print("Usage: python your_program.py <port_number>")
    sys.exit(1)

try:
    server_port = int(sys.argv[1])  # Use the provided port number
except ValueError:
    print("Invalid port number. Please provide a valid integer.")
    sys.exit(1)

# Instance of the key-value store
# Create an instance of the key-value store for this specific server port
kv_store = InMemoryKeyValueStore(server_port)
# Start the auto-saving thread
auto_save_thread = threading.Thread(target=kv_store.auto_save_thread)
auto_save_thread.daemon = True  # This thread will exit when the main program exits
auto_save_thread.start()


server_address = ("127.0.0.1", server_port)

# Bind the server to the address and port
server.bind(server_address)

# Listen for incoming connections
server.listen()
print("Listening on", server_address)

def handle_client2(client_socket, client_address):
    with client_handler_semaphore: 
        connected = True
        while connected:
            # Receive the request from the client
            request = client_socket.recv(1024)
            
            if request:
                # Deserialize the request
                request_data = pickle.loads(request)
                request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                # Determine which node is responsible for this key
                responsible_node = ring.get_node(request_data["key"])
                # print("responsible node:", responsible_node)

                # Check if the responsible node is this server
                if responsible_node == f"{server_address[0]}:{server_address[1]}":
                    # Handle the request locally
                    if request_data["action"] == "put":
                        result = kv_store.put(request_data["key"], request_data["value"])
                    elif request_data["action"] == "get":
                        result = kv_store.get(request_data["key"])
                    elif request_data["action"] == "delete":
                        result = kv_store.delete(request_data["key"])
                    elif request_data["action"] == "exit":
                        # Save and close the connection
                        kv_store.save_to_disk()
                        result = "Closing connection with server"
                        connected = False
                    else:
                        result = "Unknown Command Passed"
                else:
                    # Forward the request to the responsible node
                    print(f"Request Forwarded to Server {responsible_node} from {server_address}")
                    result = kv_store.send_request_to_node(responsible_node, request_data)

                # Serialize and send the response back to the client
                response = pickle.dumps(result)
                client_socket.send(response)

                # Log the request and response with timestamps
                log_entry = f"Request Time: {request_time}\nRequest: {request_data}\nResponse: {result}\n"
                with open("request_response.log", "a") as log_file:
                    log_file.write(log_entry)

            if not request:
                # If no request, assume the client has disconnected
                connected = False

        # Close the client socket
        client_socket.close()


while True:
    client_socket, client_address = server.accept()
    print("Accepted connection from", client_address)
    client_handler = threading.Thread(target=handle_client2, args=(client_socket, client_address))
    client_handler.start()
    # handle_client(client_socket, client_address)
