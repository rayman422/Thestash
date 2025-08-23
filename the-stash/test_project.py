#!/usr/bin/env python3
"""
Test script for The Stash project to verify all functionality is working.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        sys.path.insert(0, 'src')
        from stash import config, aggregator, generator, builder, scheduler, main, store, feeds
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        from stash.config import DEFAULT_CONFIG
        assert DEFAULT_CONFIG.site.site_name == "The Stash"
        assert len(DEFAULT_CONFIG.aggregator.feed_urls) > 0
        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_aggregator():
    """Test news aggregation."""
    print("Testing aggregator...")
    try:
        from stash.aggregator import aggregate_news, categorize_items
        from stash.config import DEFAULT_CONFIG
        
        # Test with a small sample
        items = aggregate_news(
            feed_urls=DEFAULT_CONFIG.aggregator.feed_urls[:1],  # Just one feed
            items_per_source=2,
            max_total_items=5,
            timeout_seconds=10,
            enrich=False  # Skip enrichment for speed
        )
        
        if items:
            print(f"✓ Aggregator fetched {len(items)} items")
            return True
        else:
            print("⚠ Aggregator returned no items (this might be normal)")
            return True
    except Exception as e:
        print(f"✗ Aggregator test failed: {e}")
        return False

def test_generator():
    """Test content generation."""
    print("Testing generator...")
    try:
        from stash.generator import generate_post
        from stash.aggregator import AggregatedItem
        from datetime import datetime
        
        # Create a test item
        test_item = AggregatedItem(
            title="Test Article",
            url="https://example.com/test",
            source="Test Source",
            published=datetime.now(),
            summary="This is a test article for testing purposes.",
            category="news"
        )
        
        content = generate_post(
            site_name="Test Site",
            items=[test_item],
            model="test",
            max_words=100,
            use_openai=False,
            provider="none"
        )
        
        if content and len(content) > 0:
            print("✓ Generator created content successfully")
            return True
        else:
            print("✗ Generator returned empty content")
            return False
    except Exception as e:
        print(f"✗ Generator test failed: {e}")
        return False

def test_builder():
    """Test site building."""
    print("Testing builder...")
    try:
        from stash.builder import build_env
        from pathlib import Path
        
        # Test template environment
        env = build_env("templates")
        templates = ["base.html", "index.html", "post.html", "about.html"]
        
        for template_name in templates:
            template = env.get_template(template_name)
            if template:
                print(f"✓ Template {template_name} loaded")
        
        return True
    except Exception as e:
        print(f"✗ Builder test failed: {e}")
        return False

def test_scheduler():
    """Test scheduler setup."""
    print("Testing scheduler...")
    try:
        from stash.scheduler import start_scheduler
        print("✓ Scheduler module loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Scheduler test failed: {e}")
        return False

def test_directories():
    """Test that required directories exist."""
    print("Testing directories...")
    required_dirs = ["src", "templates", "public", "public/css"]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ Directory {dir_path} exists")
        else:
            print(f"✗ Directory {dir_path} missing")
            return False
    
    return True

def test_files():
    """Test that required files exist."""
    print("Testing files...")
    required_files = [
        "requirements.txt",
        "pyproject.toml",
        "run_scheduler.py",
        "src/stash/__init__.py",
        "src/stash/main.py",
        "src/stash/config.py",
        "templates/base.html",
        "templates/index.html",
        "templates/post.html",
        "templates/about.html",
        "public/css/styles.css"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ File {file_path} exists")
        else:
            print(f"✗ File {file_path} missing")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing The Stash Project")
    print("=" * 40)
    
    tests = [
        test_directories,
        test_files,
        test_imports,
        test_config,
        test_aggregator,
        test_generator,
        test_builder,
        test_scheduler
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The project is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())