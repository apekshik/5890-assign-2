import socket
# We use pickle for serialization/deserialization
import pickle
import threading  
import time

# Define the maximum number of concurrent clients to handle
MAX_CONCURRENT_CLIENTS = 5
client_handler_semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_CLIENTS)

class InMemoryKeyValueStore:
    def __init__(self, filename="key_value_store.pkl"):
        self.filename = filename
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

    def __str__(self):
        # Get the first three key-value pairs (items) from the dictionary
        first_three_items = list(self.store.items())[:3]

        if len(self.store) <= 3:
            # If there are 3 or fewer items, print the whole store
            return str(self.store)
        else:
            # If there are more than 3 items, print only the first three
            return str(dict(first_three_items))

# Instance of the key-value store
kv_store = InMemoryKeyValueStore()

# Start the auto-saving thread
auto_save_thread = threading.Thread(target=kv_store.auto_save_thread)
auto_save_thread.daemon = True  # This thread will exit when the main program exits
auto_save_thread.start()

# Create server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ("127.0.0.1", 8888)

# Bind the server to the address and port
server.bind(server_address)

# Listen for incoming connections
server.listen()
print("Listening on", server_address)

# handle_client2 is a modification of handle_client1 that doesn't have try catch blocks. 
# the try catch blocks were causing issues which are fixed with this version of the method. 
def handle_client2(client_socket, client_address):
    with client_handler_semaphore: 
        connected = True
        while connected:
            request = client_socket.recv(1024)
            
            if request:
                request_data = pickle.loads(request)
                request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                if request_data["action"] == "put":
                    result = kv_store.put(request_data["key"], request_data["value"])
                    response = pickle.dumps(result)
                    client_socket.send(response)
                elif request_data["action"] == "get":
                    result = kv_store.get(request_data["key"])
                    response = pickle.dumps(result)
                    client_socket.send(response)
                elif request_data["action"] == "delete":
                    result = kv_store.delete(request_data["key"])
                    response = pickle.dumps(result)
                    client_socket.send(response)
                elif request_data["action"] == "exit":
                    kv_store.save_to_disk()  # Save before closing
                    response = pickle.dumps("Closing connection with server")
                    result = "Closing connection with server" # do this for logging consistency. See below for log_entry
                    client_socket.send(response)
                    connected = False
                else:
                    response = pickle.dumps("Unknown Command Passed")
                    client_socket.send(response)

                # Log the request and response with timestamps
                log_entry = f"Request Time: {request_time}\nRequest: {request_data}\nResponse: {result}\n"
                with open("request_response.log", "a") as log_file:
                    log_file.write(log_entry)

        client_socket.close()

while True:
    client_socket, client_address = server.accept()
    print("Accepted connection from", client_address)
    client_handler = threading.Thread(target=handle_client2, args=(client_socket, client_address))
    client_handler.start()
    # handle_client(client_socket, client_address)
