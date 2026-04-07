import os
import uuid
import boto3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID     = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION            = os.getenv('AWS_REGION', 'eu-north-1')
S3_BUCKET             = os.getenv('AWS_S3_BUCKET_NAME')

def get_s3_client():
    return boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )


# ── Local temp dirs ──────────────────────────────────────────────────────────

def ensure_directories(*folders):
    """Create any temp directories needed for local encryption/decryption."""
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


# ── Upload pipeline ──────────────────────────────────────────────────────────

def save_uploaded_file(file, upload_folder):
    """Save the raw uploaded file to a local temp folder for hashing/encrypting."""
    original_filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{original_filename}"
    temp_input_path = os.path.join(upload_folder, unique_name)
    file.save(temp_input_path)
    return temp_input_path, original_filename


def build_encrypted_output_path(original_filename, encrypted_folder):
    """Return a local temp path where the encrypted file will be written."""
    safe_name = secure_filename(original_filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}.enc"
    return os.path.join(encrypted_folder, unique_name)


def upload_encrypted_to_s3(local_encrypted_path, original_filename):
    """
    Upload an already-encrypted local file to S3.
    Returns the S3 object key (used as `filepath` in the database).
    """
    safe_name  = secure_filename(original_filename)
    s3_key     = f"encrypted/{uuid.uuid4().hex}_{safe_name}.enc"
    s3_client  = get_s3_client()
    s3_client.upload_file(local_encrypted_path, S3_BUCKET, s3_key)
    return s3_key


# ── Download pipeline ────────────────────────────────────────────────────────

def build_decrypted_output_path(original_filename, temp_decrypted_folder):
    """Return a local temp path where the decrypted file will be written."""
    safe_name  = secure_filename(original_filename)
    unique_dir = os.path.join(temp_decrypted_folder, uuid.uuid4().hex)
    os.makedirs(unique_dir, exist_ok=True)
    return os.path.join(unique_dir, safe_name)


def download_encrypted_from_s3(s3_key, encrypted_folder):
    """
    Download an encrypted file from S3 to a local temp path.
    Returns the local temp path.
    """
    local_path = os.path.join(encrypted_folder, f"{uuid.uuid4().hex}.enc")
    s3_client  = get_s3_client()
    s3_client.download_file(S3_BUCKET, s3_key, local_path)
    return local_path


# ── Helpers ──────────────────────────────────────────────────────────────────

def remove_file_if_exists(path):
    """Safely delete a local file without raising an error if absent."""
    if path and os.path.exists(path):
        os.remove(path)


def delete_from_s3(s3_key):
    """Delete an object from S3 (used when a user deletes their file)."""
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
    except Exception:
        pass