#!/bin/bash
# ──────────────────────────────────────────────────────────────
#  EcoStore Platform — Quick Setup Script
# ──────────────────────────────────────────────────────────────
set -e

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Running migrations..."
python manage.py makemigrations store
python manage.py migrate

echo "🌱 Seeding demo data..."
python manage.py seed_demo

echo "🚀 Starting development server..."
echo ""
echo "  ➜  http://127.0.0.1:8000"
echo "  Admin: http://127.0.0.1:8000/admin"
echo "  Demo users: alice / bob (password: demo1234)"
echo ""
python manage.py runserver
