import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class NewsArticleScraper:
    def __init__(self):
        # Headers to make our scraper look like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_article(self, url):
        """
        Extract article information from a news URL
        """
        try:
            # Step 1: Download the webpage
            print(f"🔍 Fetching article from: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Check if request was successful
            
            # Step 2: Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 3: Extract article information
            article_data = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'publication_date': self._extract_date(soup),
                'author': self._extract_author(soup),
                'source': self._extract_source(url),
                'word_count': 0,
                'images': self._extract_images(soup, url)
            }
            
            # Calculate word count
            if article_data['content']:
                article_data['word_count'] = len(article_data['content'].split())
            
            print("✅ Article scraped successfully!")
            return article_data
            
        except requests.RequestException as e:
            print(f"❌ Error fetching the URL: {e}")
            return None
        except Exception as e:
            print(f"❌ Error processing the article: {e}")
            return None
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try multiple common title selectors
        title_selectors = [
            'h1',
            '.article-title',
            '.headline',
            '.entry-title',
            '[property="og:title"]',
            'title'
        ]
        
        for selector in title_selectors:
            if selector.startswith('['):
                # For attribute selectors
                element = soup.select_one(selector)
                if element:
                    return element.get('content', '').strip()
            else:
                element = soup.find(selector)
                if element and element.get_text().strip():
                    return element.get_text().strip()
        
        return "Title not found"
    
    def _extract_content(self, soup):
        """Extract main article content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Try multiple content selectors
        content_selectors = [
            '.article-content',
            '.entry-content',
            '.post-content',
            '.content',
            'article',
            '.story-body'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Get all paragraph text
                paragraphs = content_div.find_all('p')
                content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                if len(content) > 100:  # Only return if substantial content
                    return content
        
        # Fallback: get all paragraphs from the page
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        return content if content else "Content not found"
    
    def _extract_date(self, soup):
        """Extract publication date"""
        date_selectors = [
            '[property="article:published_time"]',
            '[name="pubdate"]',
            '.date',
            '.published',
            'time'
        ]
        
        for selector in date_selectors:
            if selector.startswith('['):
                element = soup.select_one(selector)
                if element:
                    return element.get('content', '').strip()
            else:
                element = soup.find(selector)
                if element:
                    # Try to get datetime attribute first, then text
                    date = element.get('datetime', '') or element.get_text().strip()
                    if date:
                        return date
        
        return "Date not found"
    
    def _extract_author(self, soup):
        """Extract article author"""
        author_selectors = [
            '[name="author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            if selector.startswith('['):
                element = soup.select_one(selector)
                if element:
                    return element.get('content', '').strip()
            else:
                element = soup.find(selector)
                if element and element.get_text().strip():
                    return element.get_text().strip()
        
        return "Author not found"
    
    def _extract_source(self, url):
        """Extract source/domain from URL"""
        try:
            domain = urlparse(url).netloc
            # Remove 'www.' if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "Unknown source"
    
    def _extract_images(self, soup, base_url):
        """Extract image URLs from the article"""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags[:5]:  # Limit to first 5 images
            src = img.get('src', '')
            if src:
                # Convert relative URLs to absolute
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    parsed_url = urlparse(base_url)
                    src = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                
                if src.startswith('http'):
                    images.append(src)
        
        return images
    
    def print_article_summary(self, article_data):
        """Print a nice summary of the scraped article"""
        if not article_data:
            print("❌ No data to display")
            return
        
        print("\n" + "="*60)
        print("📰 ARTICLE SUMMARY")
        print("="*60)
        print(f"📝 Title: {article_data['title']}")
        print(f"🌐 Source: {article_data['source']}")
        print(f"👤 Author: {article_data['author']}")
        print(f"📅 Date: {article_data['publication_date']}")
        print(f"📊 Word Count: {article_data['word_count']}")
        print(f"🖼️  Images Found: {len(article_data['images'])}")
        print(f"🔗 URL: {article_data['url']}")
        print("\n📄 Content Preview:")
        print("-" * 40)
        # Show first 500 characters of content
        content_preview = article_data['content'][:500] + "..." if len(article_data['content']) > 500 else article_data['content']
        print(content_preview)
        print("="*60)

# Test function
def test_scraper():
    """Test the scraper with some popular news sites"""
    scraper = NewsArticleScraper()
    
    # Test URLs - you can replace these with any article URLs
    test_urls = [
        "https://www.bbc.com/news",  # This will get BBC's main page
        # Add more URLs here to test
    ]
    
    print("🚀 Testing News Article Scraper")
    print("Enter a news article URL to scrape, or press Enter to quit:")
    
    while True:
        url = input("\n🔗 URL: ").strip()
        if not url:
            break
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        article_data = scraper.scrape_article(url)
        if article_data:
            scraper.print_article_summary(article_data)
        
        print("\nWant to try another URL? (Press Enter to quit, or paste another URL)")

if __name__ == "__main__":
    test_scraper()