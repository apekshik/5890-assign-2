#!/bin/bash

# Define the list of ports to search for
ports=("8888" "8889" "8890")

# Loop through the list of ports
for port in "${ports[@]}"; do
  # Use lsof to find processes using the current port
  processes=$(lsof -ti :$port)
  
  if [ -n "$processes" ]; then
    echo "Processes found on port $port: $processes"
    
    # Loop through the processes and kill them
    for pid in $processes; do
      echo "Killing process $pid using port $port"
      kill $pid
    done
  else
    echo "No processes found on port $port"
  fi
done

echo "Process cleanup completed."
