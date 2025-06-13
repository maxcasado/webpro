# Web programming project

project:
  description:
    Projet de gestion de bibliothèque en ligne, développé en JavaScript (frontend) et FastAPI (backend).
    L'application permet de gérer des livres, des emprunts et des profils utilisateurs dans une interface web complète.

features:
  - Recherche de livres par titre, auteur ou description
  - Affichage des livres disponibles avec quantité restante
  - Emprunt d’un livre (décrémente la quantité)
  - Vue "Mes emprunts" avec la date de retour
  - Prolongation d’emprunt (21 jours, une seule fois possible)
  - Gestion du profil utilisateur (modification des infos et du mot de passe)
  - Authentification sécurisée avec sessions

technologies:
  backend:
    - FastAPI
    - SQLAlchemy
    - Alembic
    - SQLite
    - Pydantic
    - Uvicorn
  frontend:
    - HTML
    - CSS
    - JavaScript
    - Bootstrap
    - Fetch API

structure:
  backend:
    - main.py: Entrée principale FastAPI
    - routers/: Fichiers de routes (books, users, loans, auth)
    - models/: Modèles SQLAlchemy
    - schemas/: Schémas Pydantic
    - services/: Logique métier
    - database.py: Connexion SQLite
    - requirements.txt: Dépendances Python
  frontend:
    - index.html: Page d'accueil
    - js/:
        - api.js: Appels API
        - books.js: Gestion des livres
        - loans.js: Gestion des emprunts
        - profile.js: Gestion du profil
    - css/style.css: Styles personnalisés

installation:
  steps:
    - step 1: >
        Cloner le dépôt :
        git clone https://github.com/maxcasado/webpro.git && cd webpro
    - step 2: >
        Backend :
        cd backend && python -m venv venv && source venv/bin/activate (ou venv\\Scripts\\activate)
        puis pip install -r requirements.txt
    - step 3: >
        Lancer le backend :
        uvicorn main:app --reload
    - step 4: >
        Frontend :
        cd .\frontend
        python -m server.py

requirements:
  - fastapi
  - uvicorn
  - sqlalchemy
  - pydantic
  - alembic
  - python-multipart
  - passlib[bcrypt]

todo:
  - Interface d’administration (ajout/suppression de livres)
  - Notifications de retards d’emprunt
  - Tests unitaires backend
  - Améliorations de sécurité (ex. rate limiting)
  - Internationalisation FR/EN

author:
  name: Max Casado
  github: https://github.com/maxcasado
