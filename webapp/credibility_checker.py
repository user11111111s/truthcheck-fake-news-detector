import re
from urllib.parse import urlparse
import requests
from datetime import datetime

class CredibilityChecker:
    def __init__(self):
        # Trusted news sources (you can expand this list)
        self.trusted_sources = {
            'reuters.com': 'High',
            'bbc.com': 'High', 
            'bbc.co.uk': 'High',
            'apnews.com': 'High',
            'pti.org.in': 'High',
            'thehindu.com': 'High',
            'indianexpress.com': 'High',
            'ndtv.com': 'Medium-High',
            'timesofindia.indiatimes.com': 'Medium-High',
            'hindustantimes.com': 'Medium-High',
            'theguardian.com': 'High',
            'cnn.com': 'Medium-High',
            'washingtonpost.com': 'High',
            'nytimes.com': 'High',
            'economist.com': 'High'
        }
        
        # Sources with known bias or credibility issues
        self.questionable_sources = {
            'dailymail.co.uk': 'Low',
            'breitbart.com': 'Low',
            'infowars.com': 'Very Low',
            'naturalnews.com': 'Very Low',
            'beforeitsnews.com': 'Very Low'
        }
        
        # Fake news indicator words/phrases
        self.fake_indicators = [
            'breaking', 'exclusive', 'shocking', 'you won\'t believe',
            'doctors hate this', 'they don\'t want you to know',
            'secret revealed', 'banned by government', 'miracle cure',
            'scientists baffled', 'explosive revelation', 'urgent warning'
        ]
        
        # Clickbait patterns
        self.clickbait_patterns = [
            r'\d+\s+(reasons|ways|things|secrets)',
            r'you won\'t believe',
            r'this\s+will\s+(shock|amaze|surprise)',
            r'number\s+\d+\s+will',
            r'doctors\s+(hate|love)\s+this',
            r'the\s+\w+\s+industry\s+doesn\'t\s+want'
        ]

    def check_source_credibility(self, url):
        """Check the credibility of a news source"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check against trusted sources
            if domain in self.trusted_sources:
                return {
                    'credibility': self.trusted_sources[domain],
                    'reason': 'Established, reputable news organization',
                    'score': self._get_credibility_score(self.trusted_sources[domain])
                }
            
            # Check against questionable sources
            if domain in self.questionable_sources:
                return {
                    'credibility': self.questionable_sources[domain],
                    'reason': 'Source has known credibility or bias issues',
                    'score': self._get_credibility_score(self.questionable_sources[domain])
                }
            
            # Unknown source - neutral rating
            return {
                'credibility': 'Unknown',
                'reason': 'Source not in our database - verify independently',
                'score': 50
            }
            
        except Exception as e:
            return {
                'credibility': 'Unknown',
                'reason': 'Could not analyze source',
                'score': 50
            }

    def analyze_content_patterns(self, title, content):
        """Analyze content for fake news patterns"""
        analysis_results = {
            'clickbait_score': 0,
            'emotional_language': 0,
            'fake_indicators': [],
            'clickbait_patterns': [],
            'overall_suspicion': 'Low'
        }
        
        full_text = (title + ' ' + content).lower()
        
        # Check for fake news indicators
        for indicator in self.fake_indicators:
            if indicator.lower() in full_text:
                analysis_results['fake_indicators'].append(indicator)
        
        # Check for clickbait patterns
        for pattern in self.clickbait_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                analysis_results['clickbait_patterns'].append(pattern)
        
        # Calculate clickbait score
        analysis_results['clickbait_score'] = min(100, 
            len(analysis_results['fake_indicators']) * 20 + 
            len(analysis_results['clickbait_patterns']) * 15
        )
        
        # Check emotional language
        emotional_words = ['shocking', 'outrageous', 'devastating', 'incredible', 
                          'unbelievable', 'amazing', 'terrifying', 'disgusting']
        emotional_count = sum(1 for word in emotional_words if word in full_text)
        analysis_results['emotional_language'] = min(100, emotional_count * 10)
        
        # Calculate overall suspicion
        total_suspicion = (analysis_results['clickbait_score'] + 
                          analysis_results['emotional_language']) / 2
        
        if total_suspicion > 60:
            analysis_results['overall_suspicion'] = 'High'
        elif total_suspicion > 30:
            analysis_results['overall_suspicion'] = 'Medium'
        else:
            analysis_results['overall_suspicion'] = 'Low'
        
        return analysis_results

    def check_article_quality(self, article_data):
        """Comprehensive article quality check"""
        quality_score = 100
        issues = []
        
        # Check word count
        word_count = article_data.get('word_count', 0)
        if word_count < 100:
            quality_score -= 20
            issues.append("Very short article (less than 100 words)")
        elif word_count < 300:
            quality_score -= 10
            issues.append("Short article (less than 300 words)")
        
        # Check for author
        author = article_data.get('author', '')
        if author == "Author not found" or not author:
            quality_score -= 15
            issues.append("No author information")
        
        # Check for date
        date = article_data.get('publication_date', '')
        if date == "Date not found" or not date:
            quality_score -= 10
            issues.append("No publication date")
        
        # Check title quality
        title = article_data.get('title', '')
        if len(title.split()) < 3:
            quality_score -= 15
            issues.append("Very short or unclear title")
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues
        }

    def _get_credibility_score(self, credibility_level):
        """Convert credibility level to numeric score"""
        scores = {
            'Very Low': 10,
            'Low': 25,
            'Medium': 50,
            'Medium-High': 75,
            'High': 90,
            'Unknown': 50
        }
        return scores.get(credibility_level, 50)

    def generate_credibility_report(self, article_data):
        """Generate a comprehensive credibility report"""
        url = article_data.get('url', '')
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        
        # Get source credibility
        source_check = self.check_source_credibility(url)
        
        # Analyze content patterns
        content_analysis = self.analyze_content_patterns(title, content)
        
        # Check article quality
        quality_check = self.check_article_quality(article_data)
        
        # Calculate overall credibility score
        source_weight = 0.4
        content_weight = 0.3
        quality_weight = 0.3
        
        overall_score = (
            source_check['score'] * source_weight +
            (100 - content_analysis['clickbait_score']) * content_weight +
            quality_check['quality_score'] * quality_weight
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'source_credibility': source_check,
            'content_analysis': content_analysis,
            'quality_analysis': quality_check,
            'recommendation': self._get_recommendation(overall_score)
        }
    
    def _get_recommendation(self, score):
        """Get recommendation based on credibility score"""
        if score >= 80:
            return {
                'level': 'High Credibility',
                'message': 'This article appears to be from a reliable source with good quality content.',
                'color': 'green'
            }
        elif score >= 60:
            return {
                'level': 'Medium Credibility',
                'message': 'This article seems generally reliable but verify important claims.',
                'color': 'orange'
            }
        elif score >= 40:
            return {
                'level': 'Low Credibility',
                'message': 'Be cautious - this article may have credibility issues.',
                'color': 'red'
            }
        else:
            return {
                'level': 'Very Low Credibility',
                'message': 'High risk of misinformation - verify through multiple reliable sources.',
                'color': 'darkred'
            }


# Test the credibility checker
if __name__ == "__main__":
    checker = CredibilityChecker()
    
    # Test with a sample article
    test_article = {
        'url': 'https://www.reuters.com/test-article',
        'title': 'Breaking: You Won\'t Believe This Shocking Discovery',
        'content': 'This amazing breakthrough will change everything...',
        'author': 'John Doe',
        'publication_date': '2024-01-15',
        'word_count': 150
    }
    
    report = checker.generate_credibility_report(test_article)
    print("Credibility Report:", report)