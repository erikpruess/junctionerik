#!/bin/bash

sqlite3 database/database.db < database/schema.sql
echo "Database updated"