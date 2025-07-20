import os

DB_PASSWORD = os.getenv("DB_PASSWORD", "YourSecurePassword1231")
SECRET_KEY = os.getenv("SECRET_KEY", "YourFlaskSecretKey4561")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'pdf', 'docx'}
MAX_FILE_SIZE_MB = 100

CATEGORIES = ["Health", "Relationships", "Career", "Personal", "Finance", "Education", "Legal", "Property", "Social", "Technology"]

