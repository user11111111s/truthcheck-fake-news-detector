import sqlite3
import json
from datetime import datetime
import os

class ArticleDatabase:
    def __init__(self, db_path="articles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the articles table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content TEXT,
                author TEXT,
                publication_date TEXT,
                source TEXT,
                word_count INTEGER,
                images TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_fake INTEGER DEFAULT NULL,
                bias_score TEXT DEFAULT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized!")
    
    def save_article(self, article_data):
        """Save scraped article to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert images list to JSON string
            images_json = json.dumps(article_data.get('images', []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (url, title, content, author, publication_date, source, word_count, images)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data['url'],
                article_data['title'],
                article_data['content'],
                article_data['author'],
                article_data['publication_date'],
                article_data['source'],
                article_data['word_count'],
                images_json
            ))
            
            article_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Article saved to database with ID: {article_id}")
            return article_id
            
        except Exception as e:
            print(f"❌ Error saving article: {e}")
            return None
    
    def get_article(self, article_id):
        """Get a specific article by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(cursor, row)
        return None
    
    def get_all_articles(self, limit=50):
        """Get all articles, newest first"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            ORDER BY scraped_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(cursor, row) for row in rows]
    
    def search_articles(self, query):
        """Search articles by title or content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY scraped_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(cursor, row) for row in rows]
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM articles')
        total_articles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT source) FROM articles')
        unique_sources = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(word_count) FROM articles WHERE word_count > 0')
        avg_word_count = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'unique_sources': unique_sources,
            'avg_word_count': round(avg_word_count, 2)
        }
    
    def _row_to_dict(self, cursor, row):
        """Convert database row to dictionary"""
        columns = [description[0] for description in cursor.description]
        article_dict = dict(zip(columns, row))
        
        # Parse images JSON back to list
        if article_dict.get('images'):
            try:
                article_dict['images'] = json.loads(article_dict['images'])
            except:
                article_dict['images'] = []
        else:
            article_dict['images'] = []
            
        return article_dict

# Test the database
if __name__ == "__main__":
    db = ArticleDatabase()
    stats = db.get_stats()
    print("Database Stats:", stats)

# // test comment