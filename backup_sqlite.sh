#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="home/user/backups/c_bot"
DB_FILE="/home/user/c_bot/db.sqlite3"

mkdir -p "$BACKUP_DIR"

# Создаём бэкап с помощью SQLite
sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3'"