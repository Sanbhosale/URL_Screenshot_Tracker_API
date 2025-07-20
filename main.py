import os
import uuid
import threading
import time
import requests
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Configuration
SCREENSHOTS_DIR = 'screenshots'
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
DATABASE_PATH = 'sqlite:///screenshots.db'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class ScreenshotJob(db.Model):
    id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String, nullable=False)
    webhook_url = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='queued')
    screenshot_path = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    failed_reason = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {
            'job_id': self.id,
            'url': self.url,
            'webhook_url': self.webhook_url,
            'status': self.status,
            'screenshot_url': f'{request.url_root}screenshots/{self.id}.png' if self.screenshot_path else None,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'failed_reason': self.failed_reason
        }

with app.app_context():
    db.create_all()

# Real screenshot capture using Selenium
def capture_screenshot(url, out_path):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(2)
        driver.save_screenshot(out_path)
        driver.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# Background worker for screenshot jobs
def process_job(job_id):
    with app.app_context():
        job = ScreenshotJob.query.get(job_id)
        if not job:
            return
        job.status = 'pending'
        db.session.commit()

        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{job_id}.png")
        success, error = capture_screenshot(job.url, screenshot_path)
        if success:
            job.status = 'completed'
            job.screenshot_path = screenshot_path
            job.completed_at = datetime.utcnow()
        else:
            job.status = 'failed'
            job.failed_reason = error
        db.session.commit()

        # Webhook notification
        if job.webhook_url:
            payload = {
                'job_id': job.id,
                'status': job.status,
                'screenshot_url': f'{request.url_root}screenshots/{job.id}.png' if job.status == 'completed' else None,
                'failed_reason': job.failed_reason
            }
            try:
                requests.post(job.webhook_url, json=payload, timeout=5)
            except Exception:
                pass

def start_background_job(job_id):
    thread = threading.Thread(target=process_job, args=(job_id,))
    thread.daemon = True
    thread.start()

# API Endpoints

@app.route('/screenshots', methods=['POST'])
def submit_screenshot():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL'}), 400

    job_id = uuid.uuid4().hex
    job = ScreenshotJob(
        id=job_id,
        url=data['url'],
        webhook_url=data.get('webhook_url')
    )
    db.session.add(job)
    db.session.commit()
    start_background_job(job_id)
    return jsonify({'job_id': job_id, 'status': 'queued'}), 202

@app.route('/screenshots/<job_id>/status', methods=['GET'])
def check_job_status(job_id):
    job = ScreenshotJob.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({'job_id': job.id, 'status': job.status})

@app.route('/screenshots/<job_id>', methods=['GET'])
def get_screenshot(job_id):
    job = ScreenshotJob.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if job.status != 'completed':
        return jsonify({'error': 'Screenshot not completed yet', 'status': job.status}), 400
    return jsonify({
        'job_id': job.id,
        'url': job.url,
        'status': job.status,
        'screenshot_url': f'{request.url_root}screenshots/{job.id}.png',
        'created_at': job.created_at.isoformat(),
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    })

@app.route('/screenshots/<job_id>.png', methods=['GET'])
def serve_screenshot_image(job_id):
    job = ScreenshotJob.query.get(job_id)
    if not job or not job.screenshot_path or job.status != 'completed':
        return abort(404)
    return send_from_directory(SCREENSHOTS_DIR, f"{job_id}.png")

@app.route('/admin/jobs', methods=['GET'])
def list_jobs():
    jobs = ScreenshotJob.query.order_by(ScreenshotJob.created_at.desc()).all()
    return jsonify([job.to_dict() for job in jobs])

@app.route('/')
def home():
    return """
    <h2>Screenshot API is running!</h2>
    <p>Use <b>/screenshots</b> endpoint to submit screenshot jobs.<br>
    Try this with Python, Postman, or curl.<br>
    <br>
    Example Endpoints:<br>
    <ul>
      <li>POST /screenshots</li>
      <li>GET /screenshots/&lt;job_id&gt;/status</li>
      <li>GET /screenshots/&lt;job_id&gt;</li>
      <li>GET /screenshots/&lt;job_id&gt;.png</li>
      <li>GET /admin/jobs</li>
    </ul>
    </p>
    """

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
