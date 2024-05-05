#!/bin/bash

# Step 1: Export environment variables from .env.prod.db and .env.prod
export $(grep -v '^#' .env.prod.db | xargs)
export $(grep -v '^#' .env.prod | xargs)

# Step 2: Check if a command line argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [number_of_rows]"
    exit 1
fi

# Step 3: Run the Python script with the provided argument
python3 load_data.py "$1"
