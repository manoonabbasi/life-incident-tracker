# 📝 Life Incident Tracker

A simple Flask-based application to **log and manage every incident in your life** with categories, attachments, and filters.

## 🚀 Features

- Add, view, edit, and delete incidents
- Filter by year, month, category, or search text
- Upload and view attachments (PDF, images, documents)
- Modern responsive UI (HTML, CSS)
- SQLite database secured with SQLCipher
- Dockerized for easy deployment

## 🗂️ Categories Included

- Health
- Relationships
- Career
- Finance
- Education
- Legal
- Personal Development
- Travel
- Spiritual/Religious
- Property
- Social
- Technology
- Other

## ⚙️ Installation & Usage

### Clone Repository

git clone https://github.com/manoonabbasi/life-incident-tracker.git
cd life-incident-tracker

### Build Docker Image

docker build -t incident-tracker:latest .

### Run with Docker Compose

docker compose up -d

### Access the App

http://localhost:5032

## 📁 Project Structure

app.py  
config.py  
requirements.txt  
Dockerfile  
docker-compose.yml  
templates/  
static/  
uploads/

## 🔐 Security Notes

Update DB_PASSWORD and SECRET_KEY in config.py before production use.  
Use HTTPS and a reverse proxy for secure deployment.

## 📝 License

MIT License

## 🙌 Contributions

PRs are welcome. Feel free to fork and enhance features, UI, or deployment workflows.

### ✨ Author

Developed by mahmed
