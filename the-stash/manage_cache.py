#!/usr/bin/env python3
"""
Utility script for managing The Stash cache and maintenance tasks.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

def clear_seen_urls():
    """Clear the seen URLs cache to allow re-processing of content."""
    cache_file = Path("content/seen_urls.json")
    if cache_file.exists():
        cache_file.unlink()
        print("✅ Cleared seen URLs cache")
    else:
        print("ℹ️  No seen URLs cache found")

def show_cache_stats():
    """Show statistics about the current cache."""
    cache_file = Path("content/seen_urls.json")
    history_file = Path("content/history.json")
    
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            seen_urls = json.load(f)
        print(f"📊 Seen URLs: {len(seen_urls)}")
    else:
        print("📊 Seen URLs: 0 (no cache)")
    
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
        print(f"📊 Posts in history: {len(history)}")
        
        if history:
            latest = history[0]
            print(f"📅 Latest post: {latest.get('title', 'Unknown')}")
            print(f"📅 Latest post date: {latest.get('created_at', 'Unknown')}")
    else:
        print("📊 Posts in history: 0 (no history)")

def clean_old_posts(days=7):
    """Remove posts older than specified days."""
    history_file = Path("content/history.json")
    if not history_file.exists():
        print("ℹ️  No history file found")
        return
    
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    cutoff_date = datetime.now() - timedelta(days=days)
    original_count = len(history)
    
    # Filter out old posts
    history = [
        post for post in history 
        if datetime.fromisoformat(post['created_at'].replace('Z', '+00:00')) > cutoff_date
    ]
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    removed = original_count - len(history)
    print(f"🗑️  Removed {removed} posts older than {days} days")
    print(f"📊 Remaining posts: {len(history)}")

def show_site_stats():
    """Show statistics about the generated site."""
    site_dir = Path("site")
    posts_dir = site_dir / "posts"
    
    if not site_dir.exists():
        print("❌ Site directory not found")
        return
    
    # Count HTML files
    html_files = list(site_dir.glob("*.html"))
    post_files = list(posts_dir.glob("*.html")) if posts_dir.exists() else []
    
    print(f"📁 Site files: {len(html_files)}")
    print(f"📁 Post files: {len(post_files)}")
    
    # Check for CSS
    css_file = site_dir / "css" / "styles.css"
    if css_file.exists():
        print("✅ CSS file exists")
    else:
        print("❌ CSS file missing")
    
    # Check for RSS feed
    rss_file = site_dir / "feed.xml"
    if rss_file.exists():
        print("✅ RSS feed exists")
    else:
        print("❌ RSS feed missing")

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("The Stash Cache Management Utility")
        print("=" * 40)
        print("Usage:")
        print("  python3 manage_cache.py clear     - Clear seen URLs cache")
        print("  python3 manage_cache.py stats     - Show cache statistics")
        print("  python3 manage_cache.py clean     - Clean old posts (7 days)")
        print("  python3 manage_cache.py clean 30  - Clean old posts (30 days)")
        print("  python3 manage_cache.py site      - Show site statistics")
        return
    
    command = sys.argv[1]
    
    if command == "clear":
        clear_seen_urls()
    elif command == "stats":
        show_cache_stats()
    elif command == "clean":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        clean_old_posts(days)
    elif command == "site":
        show_site_stats()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()