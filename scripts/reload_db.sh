#!/usr/bin/env bash
# Run this script while being in the project's root folder, that's all I ask of you
echo "Dropping the current databases"
mongo scripts/drop_db.sh
echo "Loading the database from dump archive"
bash scripts/load_db.sh