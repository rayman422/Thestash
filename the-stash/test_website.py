#!/usr/bin/env python3
"""
Comprehensive website test script for The Stash.
"""

import requests
import time
import sys
from pathlib import Path

def test_server_connection():
    """Test if the server is running and accessible."""
    print("Testing server connection...")
    try:
        response = requests.head("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_main_page():
    """Test the main page loads correctly."""
    print("Testing main page...")
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "The Stash" in content and "Peace, Love, and Lifted News" in content:
                print("✅ Main page loads correctly with content")
                return True
            else:
                print("❌ Main page missing expected content")
                return False
        else:
            print(f"❌ Main page returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error loading main page: {e}")
        return False

def test_css_loading():
    """Test if CSS loads correctly."""
    print("Testing CSS loading...")
    try:
        response = requests.get("http://localhost:8080/css/styles.css", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "site-header" in content and "post-list" in content:
                print("✅ CSS loads correctly with expected styles")
                return True
            else:
                print("❌ CSS missing expected styles")
                return False
        else:
            print(f"❌ CSS returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error loading CSS: {e}")
        return False

def test_post_pages():
    """Test if post pages load correctly."""
    print("Testing post pages...")
    try:
        # Get the main page to find post links
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code != 200:
            print("❌ Cannot load main page to find posts")
            return False
        
        content = response.text
        # Look for post links
        if "posts/" not in content:
            print("❌ No post links found on main page")
            return False
        
        # Test the first post we can find
        lines = content.split('\n')
        post_url = None
        for line in lines:
            if 'href="posts/' in line:
                start = line.find('href="posts/') + 6
                end = line.find('"', start)
                post_url = line[start:end]
                break
        
        if not post_url:
            print("❌ No post URL found")
            return False
        
        print(f"Testing post: {post_url}")
        response = requests.get(f"http://localhost:8080/{post_url}", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "The Stash Roundup" in content and "Sources" in content:
                print("✅ Post page loads correctly with content")
                return True
            else:
                print("❌ Post page missing expected content")
                return False
        else:
            print(f"❌ Post page returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing post pages: {e}")
        return False

def test_navigation():
    """Test if navigation links work."""
    print("Testing navigation...")
    try:
        # Test about page
        response = requests.get("http://localhost:8080/about.html", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "About The Stash" in content:
                print("✅ About page loads correctly")
            else:
                print("❌ About page missing expected content")
                return False
        else:
            print(f"❌ About page returned status code: {response.status_code}")
            return False
        
        # Test RSS feed
        response = requests.get("http://localhost:8080/feed.xml", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "rss" in content and "The Stash" in content:
                print("✅ RSS feed loads correctly")
            else:
                print("❌ RSS feed missing expected content")
                return False
        else:
            print(f"❌ RSS feed returned status code: {response.status_code}")
            return False
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing navigation: {e}")
        return False

def test_file_structure():
    """Test if all required files exist."""
    print("Testing file structure...")
    site_dir = Path("site")
    required_files = [
        "index.html",
        "about.html", 
        "css/styles.css",
        "feed.xml",
        "sitemap.xml",
        "robots.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (site_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def main():
    """Run all website tests."""
    print("🌐 Testing The Stash Website")
    print("=" * 50)
    
    tests = [
        test_server_connection,
        test_file_structure,
        test_main_page,
        test_css_loading,
        test_post_pages,
        test_navigation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All website tests passed! The site is fully functional.")
        print("\n🌐 Website is ready at: http://localhost:8080")
        return 0
    else:
        print("❌ Some website tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())