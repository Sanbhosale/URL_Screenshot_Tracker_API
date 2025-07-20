# URL Screenshot Tracker API

A **backend service** to capture website screenshots asynchronously, built using Flask, Selenium, and SQLAlchemy. Users can submit URLs for screenshot generation, track job status, and receive webhook notifications upon completion.

---

## Features

- **Asynchronous processing** of screenshot jobs (non-blocking requests)
- **Webhook notifications** upon job completion
- **Public URLs** to access generated screenshots
- **Job status tracking** endpoints
- **Admin endpoint** to list all submitted jobs

---

## How It Works

1. Users **submit a URL** via the `/screenshots` endpoint along with an optional `webhook_url`.
2. The API **queues the job** and returns a job ID immediately.
3. In the background, **Selenium with headless Chrome** captures the website screenshot.
4. The job status is updated in the database:
   - `queued` → `pending` → `completed` or `failed`
5. Upon completion, the system **sends a POST request to the provided webhook URL** with the job status and screenshot URL.
6. Users can **check status anytime** and download the screenshot using its public URL.

---

## Tech Stack

- **Python**
- **Flask** – API framework
- **SQLAlchemy** – ORM for database management
- **Selenium** – automated headless browser for screenshots
- **Requests** – HTTP client for webhook notifications
- **Threading** – for background asynchronous processing

---

## Key Highlights

✔ Implements **real-world asynchronous workflows** using background threads  
✔ Uses **headless Chrome and Chromedriver** for high-quality screenshots  
✔ Designed with **clean, RESTful API endpoints**  
✔ Includes a **dedicated test script (`Test.py`)** to automate job submission and result validation

---

## Instructions to Run and Test the App

1. Run the Flask app

- python main.py (on terminal)
- python Test.py (on terminal)
   
---

## Sample output

  Submitted https://example.com → Job ID: abc123
  Attempt 1: status = pending
  Attempt 2: status = completed
  Screenshot saved as ./example_com_abc123_20250718_205923.png

  ---

### Sample Console Output

Below is a sample output when running `python main.py`:

<img width="1919" height="1017" alt="Screenshot 2025-07-21 004135" src="https://github.com/user-attachments/assets/2cadfe2b-a1ad-4387-8402-e611f98a8782" />


Below is a sample output when running `python Test.py`:

<img width="1919" height="1020" alt="Screenshot 2025-07-20 225838" src="https://github.com/user-attachments/assets/192a320e-e090-4e13-8c4b-aba47d3bcbb7" />

---

## Using Postman

## **POST /screenshots**

- **Method:** POST  
- **URL:** `http://127.0.0.1:5000/screenshots`  

---

## **GET /screenshots/<job_id>/status**

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/screenshots/<job_id>/status`  

---

## **GET /screenshots/<job_id>**

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/screenshots/<job_id>` 

---

## **GET /screenshots/<job_id>.png**

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/screenshots/<job_id>.png` 







