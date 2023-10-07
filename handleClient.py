# Function to handle client requests
import socket
# We use pickle for serialization/deserialization
import pickle
import threading  

class InMemoryKeyValueStore:
    def __init__(self):
        self.store = {}

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

def handle_client(client_socket, client_address):
    connected = True
    while connected: 
        request = client_socket.recv(1024)  # Receive data from the client
        # print("request: ", request)
        try:
            request_data = pickle.loads(request)  # Deserialize the request
            print("request_data: ", request_data)

            # handle request
            if request_data["action"] == "put":
                result = kv_store.put(request_data["key"], request_data["value"])
                print("result: ", result)
                response = pickle.dumps(result)
                client_socket.send(response)
            elif request_data["action"] == "get":
                result = kv_store.get(request_data["key"])
                print("result: ", result)
                response = pickle.dumps(result)  # Serialize the response
                client_socket.send(response)  # Send the response to the client
            elif request_data["action"] == "delete":
                kv_store.delete(request_data["key"])
                response = pickle.dumps("Deleted a key-value")  # Send a response indicating deletion
                client_socket.send(response)  # Send the response to the client
            elif request_data["action"] == "exit":
                response = pickle.dumps("Closing connection with server")
                client_socket.send(response)    
                connected = False
            else: 
                response = pickle.dumps("Unknown Command Passed")
                client_socket.send(response)
        except Exception as e:
            print("Error handling client request:", e)
        finally:
            print("kv_store currently looks like: ", kv_store)
    client_socket.close()

