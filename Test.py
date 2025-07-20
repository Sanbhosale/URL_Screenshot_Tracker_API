import requests
import time
import datetime
from urllib.parse import urlparse

API = "http://127.0.0.1:5000"
URLS = [
    "https://dribbble.com",
    "https://example.com"
]

MAX_ATTEMPTS = 10
DELAY_SECONDS = 2

def generate_filename(url, job_id):
    domain = urlparse(url).netloc.replace(".", "_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{domain}_{job_id}_{timestamp}.png"

for target in URLS:
    payload = {
        "url": target,
        "viewport": "1280,720",
        "force": True
    }

    try:
        resp = requests.post(f"{API}/screenshots", json=payload)
        resp.raise_for_status()
        job_id = resp.json()["job_id"]
        print(f"📤 Submitted {target} → Job ID: {job_id}")
    except requests.exceptions.RequestException as e:
        print(f"🚨 Failed to submit {target}: {e}")
        continue

    for attempt in range(MAX_ATTEMPTS):
        time.sleep(DELAY_SECONDS)
        try:
            status_resp = requests.get(f"{API}/screenshots/{job_id}/status")
            status_resp.raise_for_status()
            status = status_resp.json().get("status")
            print(f"⏳ Attempt {attempt+1}: {status}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Status check failed on attempt {attempt+1}: {e}")
            continue

        if status == "completed":
            try:
                img = requests.get(f"{API}/screenshots/{job_id}.png")
                img.raise_for_status()
                filename = generate_filename(target, job_id)
                with open(filename, "wb") as f:
                    f.write(img.content)
                print(f"✅ Screenshot saved as {filename}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to download screenshot: {e}")
            break

        elif status == "failed":
            print("❌ Screenshot job failed.")
            break
    else:
        print("⌛ Screenshot not ready after max attempts.")
