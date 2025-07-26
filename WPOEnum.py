#!/usr/bin/env python3
"""
WPOEnum - WordPress oEmbed Username Enumerator
Author: Davidzzo23
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlparse
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import re
from tqdm import tqdm
import argparse
import sys
import json
import csv
import time
from colorama import init, Fore, Style

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

usernames_lock = Lock()
proxies = None
headers = {}
delay_between_requests = 0.0

def print_info(msg): print(f"{Fore.CYAN}[i] {msg}{Style.RESET_ALL}")
def print_success(msg): print(f"{Fore.GREEN}[+] {msg}{Style.RESET_ALL}")
def print_warning(msg): print(f"{Fore.YELLOW}[!] {msg}{Style.RESET_ALL}")
def print_error(msg): print(f"{Fore.RED}[✖] {msg}{Style.RESET_ALL}")

def get_urls_from_sitemap(sitemap_url):
    try:
        time.sleep(delay_between_requests)
        response = requests.get(sitemap_url, verify=False, timeout=10, proxies=proxies, headers=headers)
        response.raise_for_status()
    except Exception:
        return []
    try:
        root = ET.fromstring(response.content)
        return [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    except ET.ParseError:
        return []

def validate_sitemap_index(sitemap_index_url):
    try:
        time.sleep(delay_between_requests)
        response = requests.get(sitemap_index_url, verify=False, timeout=10, proxies=proxies, headers=headers)
        response.raise_for_status()
        ET.fromstring(response.content)
        return True
    except Exception:
        print_error(f"Sitemap index not found or invalid at: {sitemap_index_url}")
        return False

def extract_post_urls_from_index(index_url):
    post_urls = []
    sitemap_links = get_urls_from_sitemap(index_url)
    print_info(f"Found {len(sitemap_links)} sitemap files")
    for sitemap in sitemap_links:
        print_info(f"Processing: {sitemap}")
        urls = get_urls_from_sitemap(sitemap)
        post_urls.extend(urls)
    return post_urls

def extract_username_from_author_url(author_url):
    try:
        path = urlparse(author_url).path
        match = re.search(r'/author/([^/]+)/', path)
        if match:
            return match.group(1)
    except:
        return None
    return None

def fetch_username(url, usernames_set, base_url):
    oembed_url = f"{base_url}/wp-json/oembed/1.0/embed?url={quote(url)}"
    try:
        time.sleep(delay_between_requests)
        r = requests.get(oembed_url, verify=False, timeout=10, proxies=proxies, headers=headers)
        r.raise_for_status()
        json_data = r.json()
        author_url = json_data.get("author_url")
        if author_url:
            username = extract_username_from_author_url(author_url)
            if username:
                with usernames_lock:
                    if username not in usernames_set:
                        usernames_set.add(username)
                        tqdm.write(f"{Fore.GREEN}[+] New username found: {username}{Style.RESET_ALL}")
    except:
        pass

def extract_usernames_multithread(post_urls, base_url, max_workers=20):
    usernames_set = set()
    print_info(f"Starting username enumeration using {max_workers} threads...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_username, url, usernames_set, base_url) for url in post_urls]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Enumerating users"):
            pass
    return usernames_set

def save_output(usernames, output_format):
    filename = f"wordpress_usernames.{output_format}"
    if output_format == "txt":
        with open(filename, "w", encoding="utf-8") as f:
            for username in sorted(usernames):
                f.write(username + "\n")
    elif output_format == "json":
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(sorted(usernames), f, indent=2)
    elif output_format == "csv":
        with open(filename, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["username"])
            for username in sorted(usernames):
                writer.writerow([username])
    print_success(f"Usernames saved to: {filename}")

def main():
    global proxies, headers, delay_between_requests

    parser = argparse.ArgumentParser(description="WPOEnum - WordPress oEmbed Username Enumerator by Davidzzo23")
    parser.add_argument("-u", "--url", required=True, help="Base URL of the WordPress site (e.g. https://example.com)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of threads (default: 20)")
    parser.add_argument("-x", "--proxy", help="Proxy to use (e.g. http://127.0.0.1:8080 or socks5://127.0.0.1:9050)")
    parser.add_argument("-o", "--output", choices=["txt", "json", "csv"], default="txt", help="Output format: txt (default), json, csv")
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds of delay between requests (default: 0)")
    parser.add_argument("--user-agent", default="WPOEnum/1.0", help="Custom User-Agent string")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    sitemap_index_url = f"{base_url}/sitemap_index.xml"
    delay_between_requests = args.delay
    headers = {"User-Agent": args.user_agent}

    print("╔═════════════════════════════════════════════════╗")
    print("║           WPOEnum by Davidzzo23                 ║")
    print("╚═════════════════════════════════════════════════╝")

    print_info(f"Target: {base_url}")
    print_info(f"Checking sitemap at: {sitemap_index_url}")
    print_info(f"User-Agent: {args.user_agent}")
    if args.delay > 0:
        print_info(f"Delay between requests: {args.delay:.2f} seconds")

    if args.proxy:
        proxies = {"http": args.proxy, "https": args.proxy}
        print_info(f"Using proxy: {args.proxy}")

    if not validate_sitemap_index(sitemap_index_url):
        print_error("Exiting: No valid sitemap found (WordPress 5.5+ is required)")
        sys.exit(1)

    post_urls = extract_post_urls_from_index(sitemap_index_url)
    print_info(f"Found {len(post_urls)} total posts")

    usernames = extract_usernames_multithread(post_urls, base_url, max_workers=args.threads)

    print_success(f"Found {len(usernames)} unique usernames")
    for username in sorted(usernames):
        print(f"{Fore.CYAN} - {username}{Style.RESET_ALL}")

    save_output(usernames, args.output)

if __name__ == "__main__":
    main()
