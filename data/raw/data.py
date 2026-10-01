import random
import time
from datetime import datetime, timedelta

# Configurations
NUM_ROWS = 1000
OUTPUT_FILE = "apache_security_test_1000.log"

# Target IPs (mix of normal users and bad actors)
ips = [
    "192.168.1.105", "10.0.0.45", "172.16.5.99", "8.8.8.8", 
    "185.220.101.5", "45.145.117.10", "103.245.12.8", "198.51.100.72"
]

# Normal Assets & Pages (Noise)
normal_traffic = [
    ("GET", "/", 200),
    ("GET", "/index.html", 200),
    ("GET", "/about-us.php", 200),
    ("GET", "/contact.php", 200),
    ("POST", "/contact.php", 302),
    ("GET", "/assets/css/bootstrap.min.css", 200),
    ("GET", "/assets/js/main.js", 200),
    ("GET", "/images/banner.jpg", 200),
    ("GET", "/images/logo.png", 200),
    ("GET", "/blog/news-update-2023", 200),
    ("GET", "/favicon.ico", 200)
]

# Attacks Configurations
sqli_attacks = [
    ("/login.php", "user=admin%27+OR+%271%27%3D%271&pass=anything", "POST"),
    ("/products.php", "cat=5+UNION+SELECT+null,username,password+FROM+users", "GET"),
    ("/api/v1/users", "id=1%27+AND+(SELECT+8221+FROM(SELECT(COUNT(*)))%20--", "GET"),
    ("/search.php", "q=%27+OR+%27a%27%3D%27a", "GET"),
    ("/items.php", "id=999+OR+sleep(5)--", "GET")
]

xss_attacks = [
    ("/search.php", "q=%3Cscript%3Ealert(document.cookie)%3C/script%3E", "GET"),
    ("/comments.php", "comment=%3Cimg+src%3Dx+onerror%3Dconfirm(1)%3E&post_id=22", "POST"),
    ("/register.php", "username=%3Csvg%2Fonload%3Dalert(%27XSS%27)%3E&email=test@test.com", "POST"),
    ("/feedback.php", "msg=%3Ciframe+src%3Djavascript%3Aalert(1)%3E", "POST")
]

path_traversals = [
    ("/download.php", "file=../../../../etc/passwd", "GET"),
    ("/file-viewer.php", "doc=..%2f..%2f..%2f..%2fwindows%2fwin.ini", "GET"),
    ("/show.php", "img=../../../../var/log/apache2/access.log", "GET"),
    ("/view.php", "path=..%252f..%252f..%252fetc%252fpasswd", "GET")
]

scanner_probes = [
    ("/.env", 404),
    ("/.git/config", 404),
    ("/wp-admin/index.php", 404),
    ("/wp-config.php.bak", 404),
    ("/phpmyadmin/index.php", 404),
    ("/config.json", 404),
    ("/backup.zip", 404),
    ("/admin/login.php", 200),
    ("/cgi-bin/test.cgi", 404)
]

user_agents_normal = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
]

user_agents_scanners = [
    "sqlmap/1.7.3#stable (https://sqlmap.org)",
    "Nikto/2.1.6 (git)",
    "Nmap Scripting Engine; https://nmap.org/book/nse.html",
    "Go-http-client/1.1",
    "Wget/1.21.1",
    "curl/7.81.0"
]

def generate_realistic_logs():
    # Start timestamp (e.g., 2 days ago)
    current_time = datetime.now() - timedelta(days=2)
    log_lines = []

    for _ in range(NUM_ROWS):
        # Time increment (realistic gap between 1 to 25 seconds)
        current_time += timedelta(seconds=random.randint(1, 25))
        timestamp_str = current_time.strftime("%d/%b/%Y:%H:%M:%S +0530")
        
        # Determine request category
        # 75% Normal Traffic, 25% Attacks
        rand_val = random.random()
        
        ip = random.choice(ips)
        ua = random.choice(user_agents_normal)
        bytes_sent = random.randint(150, 12000)

        if rand_val < 0.75:
            # 1. Normal Traffic
            method, path, status = random.choice(normal_traffic)
            query = ""
            # Randomly add normal query string to make it look real
            if path in ["/about-us.php", "/contact.php"] and random.random() > 0.5:
                query = f"?ref=google&id={random.randint(10, 99)}"
            request_uri = f"{path}{query}"
            
        elif rand_val < 0.82:
            # 2. SQL Injection Attack (7%)
            path, query, method = random.choice(sqli_attacks)
            request_uri = f"{path}?{query}" if method == "GET" else path
            status = random.choice([200, 500])  # SQLi sometimes breaks database (500)
            
        elif rand_val < 0.88:
            # 3. XSS Attack (6%)
            path, query, method = random.choice(xss_attacks)
            request_uri = f"{path}?{query}" if method == "GET" else path
            status = 200
            
        elif rand_val < 0.94:
            # 4. Path Traversal (6%)
            path, query, method = random.choice(path_traversals)
            request_uri = f"{path}?{query}"
            status = random.choice([403, 404, 200]) # 403 Forbidden is common for blocked paths
            
        else:
            # 5. Scanner Probes / Recon (6%)
            path, status = random.choice(scanner_probes)
            request_uri = path
            method = "GET"
            ua = random.choice(user_agents_scanners) # Attackers often use scanners

        # Format as Apache Combined Log
        # IP - - [Date] "Method URI HTTP/1.1" Status Bytes "Referrer" "User-Agent"
        referrer = "https://www.google.com/" if random.random() > 0.5 else "https://yourwebsite.com/"
        if rand_val >= 0.94: # Scanners usually don't have referrers
            referrer = "-"

        log_line = f'{ip} - - [{timestamp_str}] "{method} {request_uri} HTTP/1.1" {status} {bytes_sent} "{referrer}" "{ua}"'
        log_lines.append(log_line)

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(log_lines))

    print(f"Success! Generated {NUM_ROWS} rows of ultra-realistic logs in: '{OUTPUT_FILE}'")

if __name__ == "__main__":
    generate_realistic_logs()