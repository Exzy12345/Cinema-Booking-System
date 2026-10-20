import sqlite3

# Connect to your database (it will create app.db if it doesn't exist)
conn = sqlite3.connect('app.db')
cur = conn.cursor()

# Read your SQL commands from app.sql
with open('app.sql', 'r') as f:
    sql_script = f.read()

# Execute the SQL commands
cur.executescript(sql_script)

# Commit changes and close
conn.commit()
conn.close()

print("Database initialized successfully!")


#flask pallet/stablepatterns/sqlite3
#python.org/3/library/sqlite3.html