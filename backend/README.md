📌 README.md
# 🎬 CritiQ – Social Movie Review & Recommendation Platform

CritiQ is a full-featured social platform where users can:
- Review movies  
- Like, comment & repost reviews  
- Follow other users  
- Receive personalized AI-based movie recommendations  
- Chat in real-time  
- Get matched with similar taste users  

This project uses an AI-powered hybrid recommendation engine built with:
- **Embeddings (SentenceTransformer/TF-IDF)**
- **Cosine similarity**
- **User behavior signals**

---

# 🚀 Tech Stack

### **Backend**
- Django & Django REST Framework  
- PostgreSQL  
- Redis  
- Celery + Celery Beat  
- Django Channels  
- JWT Authentication  
- TMDB Movie API  
- Cloudinary for image uploads  

### **AI/ML**
- SentenceTransformer (optional)
- Scikit-Learn (TF-IDF fallback)
- Cosine similarity
- Vector embeddings storage

---

# 📂 Folder Structure



backend/
│
├── apps/
│ ├── authentication/ # JWT Auth, Users, Follows
│ ├── users/ # Preferences, Stats, Blocking, Searching
│ ├── movies/ # Movie models, interactions, signals
│ ├── reviews/ # Reviews, Likes, Comments, Reposts
│ ├── social/ # Social feed, posts
│ ├── chat/ # WebSocket chat (Channels)
│ ├── matching/ # User matching algorithm
│ └── recommendations/
│ ├── ml/ # Engine + embeddings + similarity scores
│ ├── tasks.py # Celery tasks
│ └── signals.py # Auto-trigger recommender on new activity
│
├── popcult_project/
│ ├── settings.py
│ ├── urls.py
│ ├── asgi.py # For Channels + WebSockets
│ └── wsgi.py
│
├── manage.py
└── requirements.txt


---

# 🛠 Installation Guide

## **1️⃣ Clone the Repository**
```bash
git clone https://github.com/lakshchawla28/CritiQ.git
cd CritiQ/backend

2️⃣ Create Virtual Environment
python -m venv venv


Activate:

On Windows:
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables

Create .env file inside backend/ folder:

SECRET_KEY=your_secret_key
DEBUG=True

POSTGRES_DB=critiq_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

TMDB_API_KEY=your_api_key
TMDB_BASE_URL=https://api.themoviedb.org/3

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

5️⃣ Migrate Database
python manage.py makemigrations
python manage.py migrate

6️⃣ Create Superuser
python manage.py createsuperuser

▶️ Running the Project
Option A: Run everything manually

Open 4 terminals:

Terminal 1 – Django
python manage.py runserver

Terminal 2 – Celery Worker
celery -A popcult_project worker --loglevel=info

Terminal 3 – Celery Beat
celery -A popcult_project beat --loglevel=info

Terminal 4 – Redis (Check where i stored otherwise it will throw an error)
redis-server

🎉 Option B (Recommended): Use Auto-Runner .bat File (Just chnage the location of redis file as i have entered mine so keep in mind to change it otherwise it will crash)

Just double-click:

.\run_backend.bat  (this in your terminal)

This will automatically open:

Django

Celery Worker

Celery Beat

Redis (if installed)

🧠 How AI Recommendations Work
The workflow:

User interacts with movies → signals fire

Celery task generate_recommendations_task runs

ML engine:

Embeds movie metadata

Builds user taste profile

Computes cosine similarity

Stores results in DB

API endpoint returns sorted recommendations

Users can dismiss recommendations individually

🧪 Testing the API

Open:

🔗 Swagger Docs
http://127.0.0.1:8000/api/docs/

🔗 ReDoc Documentation
http://127.0.0.1:8000/api/redoc/





🙌 Contributing

Pull requests and suggestions are always welcome!
