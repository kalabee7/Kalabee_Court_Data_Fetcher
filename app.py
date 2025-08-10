from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from scraper import CourtScraper
from database import init_db, log_query, save_case_data, update_query_status, get_recent_queries
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database when app starts
with app.app_context():
    init_db()

@app.route('/')
def index():
    """Home page with search form"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_case():
    """Handle case search requests"""
    try:
        # Get form data
        case_type = request.form.get('case_type', '').strip()
        case_number = request.form.get('case_number', '').strip()
        filing_year = request.form.get('filing_year', '').strip()
        
        # Validate input
        if not all([case_type, case_number, filing_year]):
            flash('All fields are required!', 'error')
            return redirect(url_for('index'))
        
        # Validate year
        try:
            filing_year = int(filing_year)
            if filing_year < 1950 or filing_year > 2025:
                flash('Please enter a valid filing year (1950-2025)', 'error')
                return redirect(url_for('index'))
        except ValueError:
            flash('Filing year must be a number', 'error')
            return redirect(url_for('index'))
        
        # Get client IP
        client_ip = request.remote_addr or '127.0.0.1'
        
        # Log the query
        query_id = log_query(case_type, case_number, filing_year, client_ip)
        
        # Perform scraping
        print(f"🔍 Starting search for query ID: {query_id}")
        scraper = CourtScraper()
        result = scraper.search_case(case_type, case_number, filing_year)
        
        if "error" in result:
            # Update query with error status
            update_query_status(query_id, False, result["error"])
            flash(f'Search failed: {result["error"]}', 'error')
            return render_template('results.html', 
                                 error=result["error"],
                                 search_params={
                                     'case_type': case_type,
                                     'case_number': case_number,
                                     'filing_year': filing_year
                                 })
        else:
            # Save successful result
            save_case_data(query_id, result)
            update_query_status(query_id, True)
            flash('Case information retrieved successfully!', 'success')
            return render_template('results.html', 
                                 case_data=result,
                                 search_params={
                                     'case_type': case_type,
                                     'case_number': case_number,
                                     'filing_year': filing_year
                                 })
    
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Simple dashboard showing recent queries"""
    recent_queries = get_recent_queries(20)
    return render_template('dashboard.html', queries=recent_queries)

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for programmatic access"""
    try:
        data = request.get_json()
        
        case_type = data.get('case_type')
        case_number = data.get('case_number')
        filing_year = data.get('filing_year')
        
        if not all([case_type, case_number, filing_year]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Log query
        query_id = log_query(case_type, case_number, filing_year, 
                           request.remote_addr or '127.0.0.1')
        
        # Perform search
        scraper = CourtScraper()
        result = scraper.search_case(case_type, case_number, filing_year)
        
        if "error" in result:
            update_query_status(query_id, False, result["error"])
            return jsonify(result), 400
        else:
            save_case_data(query_id, result)
            update_query_status(query_id, True)
            return jsonify({"success": True, "data": result}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "app": "Court Data Fetcher"})

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    print("🚀 Starting Court Data Fetcher...")
    print(f"🌐 Access the app at: http://localhost:5000")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
