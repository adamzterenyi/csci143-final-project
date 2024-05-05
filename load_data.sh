#!/bin/bash

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 --db <database_connection_string> [--user_rows <number_of_users>]"
  exit 1
fi

python3 load_data.py "$@"
