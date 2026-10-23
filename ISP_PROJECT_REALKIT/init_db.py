import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('netneuronix.db')
    crsr = conn.cursor()
    
    # User Table (Roles & Security)
    crsr.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    
    # Requests Table (Persistence)
    crsr.execute('''CREATE TABLE IF NOT EXISTS requests 
                 (id INTEGER PRIMARY KEY, client_name TEXT, bandwidth INTEGER, 
                  queue_name TEXT, status TEXT)''')

    # Create dummy users: Hashed Passwords satisfy Security NFR
    users = [
        ('isp_admin', generate_password_hash('isp'), 'iSP'),
        ('client_user', generate_password_hash('client'), 'client')
    ]
    crsr.executemany("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", users)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database is ready!")