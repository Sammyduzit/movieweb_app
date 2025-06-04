# 🎬 MovieWeb Gaming Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![API](https://img.shields.io/badge/API-Integrated-orange?style=for-the-badge)

**🚀 Transform your movie collection into an epic gaming experience! 🎮**

*Challenge your cinema knowledge • Compete on leaderboards • Build your movie empire*

</div>

---

## 🌟 **Overview**

MovieWeb is a **cutting-edge full-stack web application** that revolutionizes movie collection management by transforming it into an **epic gaming experience**. Built with modern **Python Flask architecture** and powered by **AI integration**, it's where technical excellence meets entertainment innovation.

<div align="center">

### ⚡ **Technical Gaming Platform**

| 🎬 **Collect & Enhance** | 🧠 **AI-Powered Battles** | 🏆 **Compete & Conquer** |
|---------------------------|----------------------------|---------------------------|
| **Smart Collection Building** | **Dynamic Trivia Generation** | **Global Competition System** |
| Auto-enhanced via OMDb API | OpenAI-powered questions | Real-time leaderboards |
| Rich metadata & posters | Adaptive difficulty levels | Performance achievements |
| Review & rating system | 7 & 21-question challenges | Social gaming features |

</div>

**🛠️ Core Architecture:**
- **Flask + SQLAlchemy** - Modular MVC design with Blueprint organization
- **RESTful API** - Complete JSON endpoints for seamless integrations  
- **External APIs** - OMDb metadata + OpenAI/RapidAPI trivia generation
- **Responsive UI** - Gaming-themed interface with modern web technologies

**🚀 Ready to deploy** - Professional codebase with robust error handling, automated fallbacks, and scalable architecture that's both technically impressive and incredibly fun to use.

<details>
<summary>📸 <strong>Click to see screenshots</strong></summary>

```
🎬 GAMING HOMEPAGE
┌─────────────────────────────────────────┐
│  ⚡ MOVIEWEB GAMING PLATFORM ⚡         │
│                                         │
│  🎯 [ENTER ARENA] 🏆 [LEADERBOARD]     │
│                                         │
│  🎮 Where Cinema Becomes Legendary 🎮  │
└─────────────────────────────────────────┘

🏟️ USER MOVIE COLLECTION
┌─────────────────────────────────────────┐
│  🎬 AVATAR (2009)    🎬 INCEPTION       │
│  📊 Rating: 8.5/10   📊 Rating: 9.2/10 │
│  🧠 [TRIVIA BATTLE]  🧠 [TRIVIA BATTLE] │
│  ⚙️ [EDIT] 🗑️ [DEL]   ⚙️ [EDIT] 🗑️ [DEL] │
└─────────────────────────────────────────┘

🧠 TRIVIA BATTLE SCREEN
┌─────────────────────────────────────────┐
│  Question 3/7: What planet is Pandora?  │
│                                         │
│  🅰️ Pandora    🅱️ Naboo               │
│  🅲 Tatooine   🅳 Endor               │
│                                         │
│  Score: 2/2 (100%) ⭐                  │
└─────────────────────────────────────────┘
```

</details>

---

## ✨ **Features**

<table>
<tr>
<td width="33%">

### 🎮 **Gaming Features**
- 🧠 **AI-Powered Trivia** - Dynamic questions via OpenAI
- 🎯 **Multiple Game Modes** - Movie (7Q) & Collection (21Q) 
- ⚡ **Real-Time Scoring** - Instant feedback & percentages
- 🏆 **Global Leaderboards** - Compete across categories
- 🏅 **Achievement System** - From "Study More" to "Movie Master"

</td>
<td width="33%">

### 🎬 **Movie Management**
- 🤖 **Smart Auto-Enhancement** - OMDb API integration
- 📊 **Rich Movie Profiles** - Complete metadata & posters
- ⭐ **Review System** - Write, edit & like reviews
- 📈 **Collection Analytics** - Size & diversity tracking
- 🎭 **Genre Categorization** - Organized movie libraries

</td>
<td width="34%">

### 🛠️ **Technical Features**
- 🌐 **RESTful API** - Complete JSON endpoints
- 📱 **Responsive Design** - Gaming-themed UI/UX
- 🔄 **External APIs** - OMDb + OpenAI integration
- 🛡️ **Error Handling** - Graceful fallbacks
- 📊 **Usage Monitoring** - API rate limiting

</td>
</tr>
</table>

---

## 🚀 **Quick Start**

### 📋 **Prerequisites**
```bash
✅ Python 3.8+
✅ pip package manager
✅ API keys (OMDb, OpenAI/RapidAPI) - Optional but recommended
```

### ⚡ **Installation**

<details>
<summary>🔧 <strong>Step-by-step setup guide</strong></summary>

**1️⃣ Clone & Navigate**
```bash
git clone <repository-url>
cd movieweb
```

**2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

**3️⃣ Environment Setup** *(Create `.env` file)*
```env
OMDB_API_KEY=your_omdb_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**4️⃣ Launch Application**
```bash
python app.py
```

**5️⃣ Start Gaming!**
```
🌐 Open: http://localhost:5002
🎮 Create account → Add movies → Start trivia battles!
```

</details>

---

## 🎯 **Usage Examples**

### 🎮 **For Gamers**
```bash
1. 🎭 Create Player Account
2. 🎬 Build Movie Collection (Auto-enhanced with OMDb API)
3. 🧠 Challenge Yourself:
   • Single Movie Trivia (7 questions)
   • Collection Battle (21 questions across your library)
4. 🏆 Climb Global Leaderboards
5. ⭐ Share Reviews & Compete with Friends
```

### 👩‍💻 **For Developers**
```bash
# Access RESTful API
GET    /api/users                     # List all users
POST   /api/users                     # Create new user
GET    /api/users/{id}/movies         # Get user's movies
POST   /api/movies/{id}/reviews       # Add movie review

# API Documentation available at: /api/
```

---

## 🏗️ **Architecture Overview**

<details>
<summary>🔍 <strong>Click to explore system architecture</strong></summary>

```
📁 PROJECT STRUCTURE
├── 🚀 app.py                 # Application entry point
├── ⚙️ config.py              # Configuration management
├── 🛡️ exceptions.py          # Custom exception classes
├── 🛣️ routes/                # Flask Blueprints
│   ├── 👥 user_routes.py     # User management
│   ├── 🎬 movie_routes.py    # Movie CRUD operations
│   ├── 💬 review_routes.py   # Review system
│   ├── 🧠 trivia_routes.py   # Trivia game logic
│   └── 🌐 api_routes.py      # RESTful API endpoints
├── 🔧 services/              # Business logic layer
│   ├── 👤 user_service.py    # User operations
│   ├── 🎭 movie_service.py   # Movie management
│   ├── 🎯 trivia_service.py  # Trivia generation & scoring
│   ├── 🤖 rapidapi_service.py # ChatGPT integration
│   └── 🎬 omdb_service.py    # Movie metadata service
├── 💾 datamanager/           # Data access layer
│   ├── 📊 data_models.py     # SQLAlchemy models
│   └── 🗄️ sqlite_data_manager.py # Database operations
└── 🛠️ utils/                 # Helper utilities
    ├── 🎭 decorators.py      # Route validation decorators
    └── 🎨 template_helpers.py # Jinja2 template functions
```

### 🔧 **Tech Stack**
| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) | Web framework & business logic |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white) SQLAlchemy | Data persistence & ORM |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) | Gaming-themed UI/UX |
| **External APIs** | OpenAI • OMDb | AI trivia • Movie metadata |

</details>

---

## 🎮 **Game Mechanics**

<div align="center">

### 🏆 **Performance Ratings**

| Score | Badge | Emoji | Description |
|-------|-------|-------|-------------|
| **90%+** | Movie Master | 🏆 | Cinema Royalty |
| **75%+** | Cinema Expert | ⭐ | Film Aficionado |
| **60%+** | Movie Buff | 🎬 | Solid Knowledge |
| **40%+** | Getting There | 🍿 | Learning Path |
| **<40%** | Study More | 📚 | Room to Grow |

### 🎯 **Game Modes**

```
🎬 MOVIE TRIVIA          🎯 COLLECTION TRIVIA
┌─────────────────┐      ┌──────────────────────┐
│   7 Questions   │      │    21 Questions      │
│   Single Movie  │      │  Across Collection   │
│   Deep Dive     │  VS  │   Broad Knowledge    │
│   Expert Level  │      │   Master Challenge   │
└─────────────────┘      └──────────────────────┘
```

</div>

---

## 📊 **API Documentation**

<details>
<summary>🌐 <strong>RESTful API Endpoints</strong></summary>

### 👥 **User Management**
```http
GET    /api/users                     # Get all users
POST   /api/users                     # Create new user
GET    /api/users/{id}                # Get specific user
```

### 🎬 **Movie Operations**
```http
GET    /api/users/{id}/movies         # Get user's movies
POST   /api/users/{id}/movies         # Add movie to user
GET    /api/movies/{id}               # Get movie with reviews
PUT    /api/movies/{id}               # Update movie details
DELETE /api/movies/{id}               # Remove movie
```

### 💬 **Review System**
```http
GET    /api/movies/{id}/reviews       # Get movie reviews
POST   /api/movies/{id}/reviews       # Add new review
PUT    /api/reviews/{id}              # Update existing review
DELETE /api/reviews/{id}              # Delete review
POST   /api/reviews/{id}/like         # Like a review
```

### 📊 **API Monitoring**
```http
GET    /api/usage                     # Current API usage stats
POST   /api/usage/reset               # Reset usage counter (testing)
GET    /api/test-apis                 # Test external API connections
```

**📖 Complete API documentation:** Visit `/api/` endpoint when running

</details>

---

## 🔧 **Configuration**

### 🔑 **API Keys Setup**

<table>
<tr>
<td width="50%">

**🎬 OMDb API** *(Movie Metadata)*
- 🌐 Get key: [omdbapi.com](http://omdbapi.com)
- ✨ Enhances movies with posters, plots, ratings
- 🆓 Free tier: 1000 requests/day

</td>
<td width="50%">

**🤖 AI APIs** *(Trivia Generation)*
- 🚀 RapidAPI: [rapidapi.com](https://rapidapi.com)
- 🧠 OpenAI: [openai.com](https://openai.com)
- 🔄 Automatic fallback system

</td>
</tr>
</table>

### ⚙️ **Development Settings**
```yaml
Server: localhost:5002
Debug Mode: Enabled (development)
Database: instance/moviewebapp.sqlite
API Limits: 95 calls/month (configurable)
```

---

## 🤝 **Contributing**

<div align="center">

**🚀 We welcome contributors to make MovieWeb even more epic! 🎮**

[![Contributors Welcome](https://img.shields.io/badge/Contributors-Welcome-brightgreen?style=for-the-badge&logo=github)](https://github.com)

</div>

### 🛠️ **Development Workflow**

```bash
1. 🍴 Fork the repository
2. 🌟 Create feature branch: git checkout -b feature/amazing-feature
3. ✨ Make your magic happen
4. 🧪 Test thoroughly across browsers
5. 📝 Commit: git commit -m 'Add amazing feature'
6. 🚀 Push: git push origin feature/amazing-feature
7. 🎉 Open Pull Request
```

### 📋 **Code Standards**
- ✅ **PEP 8** compliance for Python
- 📖 **Docstrings** for all public methods
- 🛡️ **Error handling** for external APIs
- 🔍 **Descriptive** commit messages
- 🌐 **Cross-browser** testing

---

## 📄 **License**

<div align="center">

![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

This project is licensed under the **MIT License** - see the `LICENSE` file for details.

</div>

---

<div align="center">

## 🎬 **Ready to Enter the Arena?** 🎮

**Experience the future of movie collection management!**

[![Start Gaming](https://img.shields.io/badge/🚀%20START%20GAMING-Launch%20App-blue?style=for-the-badge&logo=rocket)](http://localhost:5002)
[![API Status](https://img.shields.io/badge/📊%20API%20STATUS-Check%20Now-orange?style=for-the-badge&logo=activity)]()
[![Leaderboard](https://img.shields.io/badge/🏆%20LEADERBOARD-Top%20Players-gold?style=for-the-badge&logo=trophy)]()

---

*Built with ❤️ for movie lovers and gaming enthusiasts* 

**🎭 Where every movie becomes an adventure** • **🧠 Where knowledge becomes legendary** • **🏆 Where players become champions**

</div>
