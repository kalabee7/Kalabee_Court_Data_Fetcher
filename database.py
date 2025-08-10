import sqlite3
from datetime import datetime
from config import Config
import json

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(Config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create queries table to log all search attempts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_type TEXT NOT NULL,
            case_number TEXT NOT NULL,
            filing_year INTEGER NOT NULL,
            query_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT FALSE,
            error_message TEXT,
            ip_address TEXT
        )
    ''')
    
    # Create case_data table to store successful results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id INTEGER,
            petitioner TEXT,
            respondent TEXT,
            filing_date TEXT,
            next_hearing_date TEXT,
            case_status TEXT,
            pdf_links TEXT,  -- JSON string of PDF links
            raw_html TEXT,   -- Store raw HTML for debugging
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES queries (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def log_query(case_type, case_number, filing_year, ip_address='127.0.0.1'):
    """Log a search query and return the query ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO queries (case_type, case_number, filing_year, ip_address)
        VALUES (?, ?, ?, ?)
    ''', (case_type, case_number, filing_year, ip_address))
    
    query_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"📝 Logged query ID: {query_id}")
    return query_id

def update_query_status(query_id, success, error_message=None):
    """Update the status of a query"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE queries 
        SET success = ?, error_message = ?
        WHERE id = ?
    ''', (success, error_message, query_id))
    
    conn.commit()
    conn.close()

def save_case_data(query_id, case_data):
    """Save successful case data to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert PDF links list to JSON string
    pdf_links_json = json.dumps(case_data.get('pdf_links', []))
    
    cursor.execute('''
        INSERT INTO case_data 
        (query_id, petitioner, respondent, filing_date, next_hearing_date, 
         case_status, pdf_links, raw_html)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        query_id,
        case_data.get('petitioner', ''),
        case_data.get('respondent', ''),
        case_data.get('filing_date', ''),
        case_data.get('next_hearing_date', ''),
        case_data.get('status', ''),
        pdf_links_json,
        case_data.get('raw_html', '')
    ))
    
    conn.commit()
    conn.close()
    print("💾 Case data saved successfully!")

def get_recent_queries(limit=10):
    """Get recent queries for dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT q.*, c.petitioner, c.respondent 
        FROM queries q
        LEFT JOIN case_data c ON q.id = c.query_id
        ORDER BY q.query_timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    queries = cursor.fetchall()
    conn.close()
    return queries
