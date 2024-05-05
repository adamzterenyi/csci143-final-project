#!/bin/bash

python3 load_data.py --db=postgresql://postgres:pass@localhost:5432/devdb  --user_rows=100
