import urllib.request
import urllib.error
import ssl

# Create unverified SSL context for macOS compatibility
context = ssl._create_unverified_context()

links = [
    "https://bagewadirahulr-byte.github.io/web-dev-portfolio/",
    "https://bagewadirahulr-byte.github.io/web-dev-portfolio/portfolio/index.html",
    "https://bagewadirahulr-byte.github.io/web-dev-portfolio/project1-weather/index.html",
    "https://bagewadirahulr-byte.github.io/web-dev-portfolio/project2-taskmanager/index.html",
    "https://bagewadirahulr-byte.github.io/web-dev-portfolio/project3-quiz/index.html",
    "https://snapurl-qd00.onrender.com",
    "https://linkedin.com/in/rahul-r-bagewadi-4279012a7/",
    "https://github.com/bagewadirahulr-byte",
    "https://www.instagram.com/rahul__bagewadi?igsh=MXMxd3cya3M4MnFkZg%3D%3D"
]


for url in links:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        })
        res = urllib.request.urlopen(req, context=context, timeout=10)
        print(f"[OK] {res.status} - {url}")
    except urllib.error.HTTPError as e:
        print(f"[WARN] {e.code} - {url} (Expected for some restrictive sites)")
    except Exception as e:
        print(f"[ERROR] {str(e)} - {url}")
