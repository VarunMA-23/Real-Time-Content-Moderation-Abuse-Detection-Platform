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

# Run Alembic migrations (for PostgreSQL in production)
# Falls back to create_all for SQLite local dev
alembic upgrade head 2>/dev/null || python -c "
from app.db.base import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)
print('Tables created via Base.metadata.create_all()')
"

# Seed data
python /app/scripts/seed_db.py
