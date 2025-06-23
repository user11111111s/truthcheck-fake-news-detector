from credibility_checker import CredibilityChecker
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os

# Add the scraper directory to Python path...
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scraper'))

from news_scraper import NewsArticleScraper
from database import ArticleDatabase

app = Flask(__name__)
scraper = NewsArticleScraper()
db = ArticleDatabase()

@app.route('/')
def index():
    """Home page with URL input form"""
    stats = db.get_stats()
    return render_template('index.html', stats=stats)
# Add this after creating the scraper and db instances
credibility_checker = CredibilityChecker()

@app.route('/scrape', methods=['POST'])
def scrape_article():
    """Scrape article from submitted URL with credibility analysis"""
    try:
        url = request.form.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Please provide a URL'}), 400
        
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Scrape the article
        article_data = scraper.scrape_article(url)
        
        if not article_data:
            return jsonify({'error': 'Failed to scrape article. Please check the URL.'}), 400
        
        # Generate credibility report
        credibility_report = credibility_checker.generate_credibility_report(article_data)
        
        # Save to database with credibility data
        article_id = db.save_article_with_credibility(article_data, credibility_report)
        article_data['id'] = article_id
        article_data['credibility_report'] = credibility_report
        
        return render_template('results.html', article=article_data)
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
@app.route('/history')
def history():
    """Show all scraped articles"""
    articles = db.get_all_articles()
    stats = db.get_stats()
    return render_template('history.html', articles=articles, stats=stats)

@app.route('/article/<int:article_id>')
def view_article(article_id):
    """View a specific article"""
    article = db.get_article(article_id)
    if not article:
        return "Article not found", 404
    return render_template('results.html', article=article)

@app.route('/search')
def search():
    """Search articles"""
    query = request.args.get('q', '').strip()
    if query:
        articles = db.search_articles(query)
        return render_template('history.html', articles=articles, query=query, stats=db.get_stats())
    return redirect(url_for('history'))

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(db.get_stats())

if __name__ == '__main__':
    print("🚀 Starting TruthCheck Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)