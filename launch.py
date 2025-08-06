import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    requirements = [
        'fastapi==0.104.1',
        'uvicorn==0.24.0',
        'sqlalchemy==2.0.23',
        'python-jose[cryptography]==3.3.0',
        'passlib[bcrypt]==1.7.4',
        'python-multipart==0.0.6',
        'pydantic==2.5.0'
    ]
    
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])

def setup_database():
    """Initialize SQLite database for EHS Journal"""
    db_path = Path('ehs_journal.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'Technician',
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create chemical inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chemical_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chemical_name TEXT NOT NULL,
            cas_number TEXT,
            lot_number TEXT,
            expiry_date DATE,
            quantity REAL,
            unit TEXT,
            location TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user (password: admin123!)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, hashed_password, role)
        VALUES ('admin', 'admin@ehslabs.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewmjuTrNk8gLq6FW', 'Admin')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def start_server():
    """Start the EHS Electronic Journal server"""
    print("🚀 Starting EHS Electronic Journal System...")
    print("📍 Server will be available at: http://localhost:8000")
    print("👤 Login: admin / admin123!")
    print("⏰ Current Time (EST): " + "08/05/2025 4:39 PM")
    
    # Start uvicorn server
    os.system('uvicorn main:app --host 0.0.0.0 --port 8000 --reload')

def main():
    print("🔬 EHS Electronic Journal System Launcher")
    print("=" * 50)
    
    try:
        print("📦 Installing dependencies...")
        install_requirements()
        
        print("🗄️ Setting up database...")
        setup_database()
        
        print("🎯 All systems ready!")
        start_server()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try installing Python 3.8+ and pip first")

if __name__ == '__main__':
    main()