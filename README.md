# WPOEnum

WPOEnum is a WordPress username enumeration tool that leverages public XML sitemaps and the oEmbed API to extract author information without authentication. It is designed for stealthy and efficient reconnaissance, even against targets protected by basic WAFs or rate limiting.

---

## Description

WPOEnum automates the process of harvesting WordPress usernames by chaining two publicly available features introduced in WordPress 5.5 and above:

- **Sitemap Index** (`/sitemap_index.xml`)
- **oEmbed Endpoint** (`/wp-json/oembed/1.0/embed`)

> Note: Starting with WordPress 5.5, WordPress automatically generates a sitemap index containing all public posts and publicly queryable post types and taxonomies. This file is located at /sitemap_index.xml and is designed to improve search engine discoverability — but also exposes a convenient entry point for enumeration.
> 

The tool scans all URLs listed in sitemap files, queries each via oEmbed, and extracts usernames from the `author_url` field. It supports multithreaded execution, custom user-agents, request delay, proxy routing, and output formats like TXT, JSON, and CSV.

This method is especially useful during:

- OSINT and passive reconnaissance
- Penetration testing and red teaming
- Detection of misconfigured or overexposed WordPress installations

---

## Usage

### Basic scan:

```bash
python3 wpoenum.py -u <https://targetsite.com>
```

### Enable evasion (proxy, custom user-agent, delay):

```python
python3 wpoenum.py -u https://targetsite.com -x socks5://127.0.0.1:9050 --user-agent "Mozilla/5.0 (ReconBot)" --delay 1.5
```

### Save output to JSON or CSV:

```python
python3 wpoenum.py -u https://targetsite.com -o json
python3 wpoenum.py -u https://targetsite.com -o csv
```

---

## Example Output

```python
╔═════════════════════════════════════════════════╗
║           WPOEnum by Davidzzo23                 ║
╚═════════════════════════════════════════════════╝
[i] Target: https://www.example.com
[i] Checking sitemap at: https://www.example.com/sitemap_index.xml
[i] Found 14 sitemap files
[i] Processing: https://www.example.com/post-sitemap.xml

<SNIP>

[i] Found 282 total posts
[i] Starting username enumeration using 20 threads...
[+] New username found: alice                                             
[+] New username found: bob                

[+] Found 2 unique usernames
 - alice
 - bob
[+] Usernames saved to: wordpress_usernames.txt
```

---

## Disclaimer

WPOEnum is intended for authorized security testing and educational purposes only. Unauthorized use of this tool against systems without permission is strictly prohibited.
The author assumes no liability for any misuse or damage caused by this tool.
