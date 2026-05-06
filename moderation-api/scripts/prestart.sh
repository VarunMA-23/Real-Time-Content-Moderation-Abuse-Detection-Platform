#!/usr/bin/env bash

# Let the DB start
python -c "
import socket
import time
import os

host = os.getenv('POSTGRES_SERVER', 'db')
port = 5432
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except socket.error:
        time.sleep(1)
"

# Create tables (for local dev, we use this instead of alembic for now to keep it simple)
python -c "
from app.db.base import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)
"

# Seed data
python /app/scripts/seed_db.py
