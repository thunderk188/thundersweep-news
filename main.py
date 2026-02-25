import feedparser
from datetime import datetime
from dateutil import parser
import pytz
from jinja2 import Environment, FileSystemLoader
import os

# List of top cybersecurity RSS feeds
FEEDS = [
    {"url": "https://feeds.feedburner.com/TheHackersNews", "name": "The Hacker News"},
    {"url": "https://www.bleepingcomputer.com/feed/", "name": "BleepingComputer"},
    {"url": "https://krebsonsecurity.com/feed/", "name": "Krebs on Security"},
    {"url": "https://www.darkreading.com/rss.xml", "name": "Dark Reading"},
    {"url": "https://threatpost.com/feed/", "name": "Threatpost"}
]

AD_FREQUENCY = 7 # Inject an ad every 7 articles

def fetch_and_parse_feeds():
    all_articles = []
    
    for feed_info in FEEDS:
        print(f"Fetching {feed_info['name']}...")
        parsed = feedparser.parse(feed_info["url"])
        
        for entry in parsed.entries[:15]: # Get top 15 from each to build the pool
            try:
                # Try to parse the published date
                published_str = entry.get('published', entry.get('updated', ''))
                if not published_str:
                    continue
                
                dt = parser.parse(published_str)
                # Ensure timezone aware
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.UTC)
                
                summary = entry.get('summary', entry.get('description', ''))
                
                all_articles.append({
                    "title": entry.get('title', 'No Title'),
                    "link": entry.get('link', '#'),
                    "published_dt": dt,
                    "published": dt.strftime('%b %d, %Y - %H:%M %Z'),
                    "summary": summary,
                    "source": feed_info["name"],
                    "is_ad": False
                })
            except Exception as e:
                print(f"Error parsing entry from {feed_info['name']}: {e}")
                
    # Sort all articles by date, newest first
    all_articles.sort(key=lambda x: x["published_dt"], reverse=True)
    
    # Take the top 50 articles
    top_articles = all_articles[:50]
    
    # Inject Ads
    final_feed = []
    for i, article in enumerate(top_articles):
        if i > 0 and i % AD_FREQUENCY == 0:
            final_feed.append({"is_ad": True})
        final_feed.append(article)
        
    return final_feed

def generate_static_site(articles):
    print("Generating HTML...")
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    
    now = datetime.now(pytz.timezone('US/Eastern'))
    
    html_output = template.render(
        articles=articles,
        last_updated=now.strftime('%B %d, %Y at %I:%M %p EST'),
        year=now.year
    )
    
    # Ensure public directory exists
    os.makedirs('public', exist_ok=True)
    
    # Write the output
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    print("Successfully generated public/index.html")

if __name__ == "__main__":
    articles = fetch_and_parse_feeds()
    generate_static_site(articles)
