#!/bin/bash

# Step 2: Check if a command line argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [number_of_rows]"
    exit 1
fi

# Step 3: Run the Python script with the provided argument
python3 load_data.py "$1"
