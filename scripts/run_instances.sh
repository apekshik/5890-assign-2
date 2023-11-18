#!/bin/bash

# Run Instance 1 on Port 8888
python3 Dist_InMemoryDataStore.py 8888 &

# Run Instance 2 on Port 8889
python3 Dist_InMemoryDataStore.py 8889 &

# Run Instance 3 on Port 8890
python3 Dist_InMemoryDataStore.py 8890 &

# Wait for all instances to finish
wait