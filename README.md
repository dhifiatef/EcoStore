 🛍️ EcoStore - AI-Powered E-Commerce Platform

EzyZip is a modern full-stack e-commerce web application built with **Django**. The platform allows users to browse products, manage orders, communicate with sellers, and receive AI-powered shopping recommendations using Google's Gemini API.

This project was developed to demonstrate backend development skills, authentication, database management, AI integration, and Django best practices.

---

# ✨ Features

## User Authentication
- User registration
- Secure login/logout
- Session management
- Protected pages

## Marketplace
- Browse available products
- Product listing
- Product details
- Search-friendly product display

## Product Management
- Add new products
- Edit existing products
- Delete products
- Upload product images

## Order System
- Create orders
- View order history
- Order details page

## AI Shopping Advisor
- Google Gemini AI integration
- Product recommendations
- Shopping assistance
- Interactive AI conversations

## Messaging
- Inbox
- Conversations between users

## User Dashboard
- Personal dashboard
- Quick access to products
- Orders overview
- Account management

## Settings
- User profile settings
- Account customization

## Admin Panel
- Django Admin
- Product management
- User management
- Order management

---

# 🛠️ Technologies Used

### Backend
- Python 3
- Django

### Database
- SQLite3

### Frontend
- HTML5
- CSS3
- Django Templates

### Authentication
- Django Authentication System

### AI
- Google Gemini API

### Version Control
- Git
- GitHub

---

# 📁 Project Structure

```
EzyZip/
│
├── ecommerce/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
│
├── store/
│   ├── templates/
│   │   └── store/
│   │       ├── dashboard.html
│   │       ├── marketplace.html
│   │       ├── products.html
│   │       ├── orders.html
│   │       ├── order_detail.html
│   │       ├── conversation.html
│   │       ├── inbox.html
│   │       ├── ai_advisor.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── settings.html
│   │       └── base.html
│   │
│   ├── management/
│   ├── templatetags/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── apps.py
│
├── media/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/EzyZip.git
```

## 2. Navigate into the project

```bash
cd EzyZip
```

## 3. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Apply migrations

```bash
python manage.py migrate
```

---

## 6. Create a superuser

```bash
python manage.py createsuperuser
```

---

## 7. Configure Gemini API

Set your API key as an environment variable.

Linux/macOS:

```bash
export GEMINI_API_KEY="your_api_key"
```

Windows:

```cmd
set GEMINI_API_KEY=your_api_key
```

Or replace:

```python
GEMINI_API_KEY = "YOUR_API_KEY"
```

inside `settings.py`.

---

## 8. Run the development server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000
```

---

# 📸 Main Pages

- Login
- Register
- Dashboard
- Marketplace
- Products
- Product Form
- Orders
- Order Details
- Inbox
- Conversations
- AI Advisor
- Settings

---

# 🔒 Authentication

The project uses Django's built-in authentication system for:

- User login
- Logout
- Session management
- Protected routes

---

# 🤖 AI Integration

The AI Advisor is powered by the Google Gemini API and helps users:

- Discover products
- Receive shopping suggestions
- Ask product-related questions
- Improve their shopping experience

---

# 🎯 Learning Objectives

This project demonstrates practical experience with:

- Django Framework
- MVC (MVT) Architecture
- Authentication & Authorization
- CRUD Operations
- Database Design
- File Uploads
- AI API Integration
- Template Inheritance
- URL Routing
- Git & GitHub
- Full-Stack Web Development

---

# 🚧 Future Improvements

- PostgreSQL support
- REST API with Django REST Framework
- Shopping cart
- Online payment integration
- Email notifications
- Product reviews and ratings
- Wishlist
- Advanced search and filtering
- Docker support
- Unit and integration tests
- Responsive mobile interface
- Real-time chat using WebSockets

---

# 👨‍💻 Author

**Atef Dhifi**

Software Engineering Student

Interested in:

- Backend Development
- Python
- Django
- REST APIs
- AI Integration
- Cloud Computing

GitHub: https://github.com/yourusername

---

