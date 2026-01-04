# 🛍️ Recova - AI-Powered E-Commerce Recommendation Engine

<div align="center">

![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?logo=scikit-learn&logoColor=white)

**A full-stack e-commerce platform featuring a production-grade ML recommendation engine with multiple algorithms.**

[Demo](#demo) • [Features](#features) • [Tech Stack](#tech-stack) • [Setup](#setup) • [Architecture](#architecture)

</div>

---

##  Project Highlights

| Feature | Description |
|---------|-------------|
| **4 Recommendation Algorithms** | Hybrid, Collaborative Filtering, Content-Based (TF-IDF), Popularity-Based |
| **Real-time Personalization** | Recommendations update based on user interactions |
| **Progressive Loading** | Skeleton UI patterns for instant perceived performance |
| **Persistent State** | Cart & wishlist survive page reloads via localStorage |

---

##  Features

### Recommendation Engine
- **Hybrid Algorithm** - Combines collaborative and content-based filtering for best results
- **Collaborative Filtering** - "Users who liked this also liked..." (user-user similarity)
- **Content-Based Filtering** - TF-IDF vectorization + cosine similarity on product features
- **Popularity-Based** - Trending products based on views and purchases

### Frontend
- **Shopping Cart** - Add/remove items, persistent across sessions
- **Wishlist** - Save favorites, move to cart functionality
- **User Dashboard** - Personalized stats, interaction history, recommendation controls
- **Skeleton Loading** - No blocking spinners, UI appears instantly
- **Modern UI** - Glassmorphism, animations with Framer Motion

### Backend
- **FastAPI** - High-performance async Python framework
- **Interaction Tracking** - Views, purchases, ratings, wishlist events
- **RESTful API** - Clean endpoints with automatic Swagger docs
- **ML Pipeline** - Scikit-learn, Pandas, NumPy for data processing

---

##  Tech Stack

### Frontend
```
React 18 • Vite • Framer Motion • React Router • Axios • Lucide Icons
```

### Backend
```
Python 3.11 • FastAPI • Scikit-learn • Pandas • NumPy • Uvicorn
```

### ML/Data Science
```
TF-IDF Vectorization • Cosine Similarity • User-Item Matrices • Collaborative Filtering
```

---

##  Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
├─────────────────────────────────────────────────────────────┤
│  Context API (User, Cart)  │  Pages  │  Components          │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  Routes          │  Services        │  ML Engine            │
│  - /products     │  - Product Svc   │  - Hybrid Recommender │
│  - /recommend    │  - Interaction   │  - Collaborative      │
│  - /interact     │    Tracker       │  - Content-Based      │
└─────────────────────────────────────────────────────────────┘
```

---

##  Setup

### Prerequisites
- Node.js 18+
- Python 3.11+

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API runs at `http://localhost:8000` (Swagger docs at `/docs`)

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173`

---

##  How the Recommendation Engine Works

### 1. Hybrid (Default)
Combines scores from collaborative and content-based filtering:
```python
final_score = (0.6 × collaborative_score) + (0.4 × content_score)
```

### 2. Collaborative Filtering
Finds users with similar interaction patterns and recommends what they liked:
```python
similarity = cosine_similarity(user_item_matrix)
recommendations = weighted_sum(similar_users_purchases)
```

### 3. Content-Based Filtering
Uses TF-IDF on product titles/descriptions to find similar items:
```python
tfidf_matrix = TfidfVectorizer().fit_transform(product_descriptions)
similar_products = cosine_similarity(tfidf_matrix)
```

### 4. Popularity-Based
Ranks products by total interactions (views + purchases + ratings).

---

##  Project Structure

```
ecomm/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic
│   │   └── ml/               # Recommendation algorithms
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components
│   │   ├── context/          # React Context (state)
│   │   └── api/              # API client
│   └── package.json
└── README.md
```

---

##  Learning Outcomes

This project demonstrates:
- Building ML recommendation systems from scratch
- Full-stack integration (React + FastAPI)
- State management patterns (Context API, localStorage)
- Performance optimization (skeleton loading, parallel API calls)
- Modern React patterns (hooks, functional components)

---

##  License

MIT License - feel free to use for learning or portfolio!

---

<div align="center">

**Built using React + FastAPI + Scikit-learn**

</div>
