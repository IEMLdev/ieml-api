#!/usr/bin/env bash
# Run this script while being in the project's root folder, that's all I ask of you

mongo scripts/drop_db.sh
mongo ieml_db data/ieml_db_loader.js
mongo ieml_db scripts/indexing.sh