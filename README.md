# priviX - Secure Vault Cloud

A full-stack, highly-secured file management network offering military-grade encrypted storage. 

Built with:
* **Fast Flask backend** (`app.py`, `file_handler.py`)
* **AWS S3 Cloud Storage** (`boto3`)
* **PostgreSQL Database** (`psycopg2`)
* **Modern HTML/CSS/JS frontend** with Glassmorphism UI

---

## 🔐 Features

### 1. End-to-End File Protection
* **AES-256 Encryption**: Every file uploaded to the vault is intercepted and encrypted at the application layer using symmetric Fernet encryption (`cryptography`) before it ever reaches cloud storage.
* **Secure Decryption**: Files remain tightly locked in the cloud. They are only decrypted temporarily in memory during a verified download request.

### 2. Cloud Storage Integration
* **AWS S3 Backend**: Utlizes Amazon Web Services to securely store encrypted file blobs for scalable, highly-available storage.
* **Smart File Handling**: Temporary server-side tracking seamlessly moves files between user uploads, the encryption engine, and AWS S3 blobs to ensure zero data leaks.

### 3. Granular Access Control
* **Secure Authentication**: Built-in login mechanisms strictly segregate user accounts using hashed credentials (`werkzeug.security`).
* **Asset Sharing Protocol**: Users can dynamically grant or revoke file access to specific usernames across the network. Only authorized users can ever download and decrypt shared assets.

### 4. Real-Time Telemetry & Visualization
* **Live Dashboard**: A beautiful, mobile-responsive interface showing overall data usage limits via dynamic donut charts, recent user activity logs, and system statuses.
* **Animated Aesthetics**: Fluid particle-network background, modern glassmorphism UI components, and intuitive UX/UI flows.

---

## 🚀 Quick Start (Recommended)
Since this app is completely integrated with AWS and PostgreSQL, the easiest way to view it is via the live deployment.

* **Live Deployment:** [View on Render](https://privix-secure-vault-cloud.onrender.com)

---

## 📖 How to Use

1. Open the dashboard in your browser.
2. Log in or create a new account.
3. Access **My Uploaded Files**:
   - Drag and drop files or click to upload securely.
   - Files are automatically encrypted and beamed to AWS.
4. Manage Files:
   - Click the **Download** icon to retrieve and automatically decrypt your file.
   - Click the **Share** icon and type a username to grant someone else securely vaulted access.
5. Access **Shared With Me**:
   - View all incoming files that your peers have shared with you.

---

## 🛠 Manual Setup (Local Development)

Run these steps from project root.

### 1) Prerequisites
* Python 3.10+ (`python --version`)
* PostgreSQL Database (or modify `db.py` to use local SQLite)
* AWS Account (S3 Bucket Credentials)

### 2) Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# Mac/Linux
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3) Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost/dbname
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=your_aws_region
AWS_S3_BUCKET_NAME=your_bucket_name
FERNET_KEY=your_base64_fernet_key
```

### 4) Start Application
```bash
python app.py
```
**Expected**: Flask running on `http://127.0.0.1:5000`.

---

## 🚨 Common Issues and Fixes

**ModuleNotFoundError: No module named 'flask'**
* Activate your backend `.venv` and run `pip install -r requirements.txt`.

**Database Connection Error**
* Verify your `DATABASE_URL` is correctly linked to an active, running PostgreSQL instance. Make sure you run the schema creations.

**AWS S3 Upload Failed**
* Ensure your `AWS_ACCESS_KEY_ID` has adequate IAM read/write permissions for the `AWS_S3_BUCKET_NAME`.

**Decryption / Fernet Key Error**
* Your `FERNET_KEY` cannot change once files are encrypted. If it changes, old files will be irrecoverable. Ensure it is a valid base-64 32-byte string.

---

## 📁 Project Structure

* `app.py` - Core Flask routing and API configuration
* `file_handler.py` - File uploading, streaming, and AWS interactions
* `utils/encryption.py` - File cipher and decryption engine
* `db.py` - PostgreSQL connection pool and queries
* `templates/` - HTML files with Jinja templating and inline CSS/JS
* `requirements.txt` - Python backend dependencies

---

## 👥 Team Members

| Name | Roll Number |
| :--- | :--- |
| Anvita Rayapati | 2024BCS-009 |
| Pooja Luhar | 2024BCS-049 |
| Sreeshma Nair | 2024BCS-073 |
| Swati Singh | 2024BCS-075 |
