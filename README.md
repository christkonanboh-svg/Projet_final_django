# COFINANCE CI Platform

Plateforme digitale de gestion de microcrédits, d'assurance mobile et de support client en temps réel pour **COFINANCE CI**.

## Stack technique

- Python 3.11+
- Django 5.x
- Django REST Framework
- JWT (SimpleJWT)
- drf-spectacular (Swagger/Redoc)
- Django Channels (WebSocket)
- SQLite (développement) / PostgreSQL (production)

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/christkonanboh-svg/Projet_final_django.git
cd Projet_final_django
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Migrations et données de démo

```bash
python manage.py migrate
python manage.py seed_db
```

### 5. Lancer le serveur

```bash
daphne -b 0.0.0.0 -p 8003 config.asgi:application
```

Le projet est accessible à l'adresse **http://127.0.0.1:8003/** (redirige automatiquement vers la page de connexion).

## URLs principales

| URL | Description |
|-----|-------------|
| **http://127.0.0.1:8003/** | Page d'accueil → redirection connexion |
| http://127.0.0.1:8003/app/login/ | Connexion |
| http://127.0.0.1:8003/app/client/dashboard/ | Interface client |
| http://127.0.0.1:8003/app/agent/dashboard/ | Interface agent |
| http://127.0.0.1:8003/app/admin/dashboard/ | Interface admin |
| http://127.0.0.1:8003/api/docs/ | Documentation Swagger |
| http://127.0.0.1:8003/api/redoc/ | Documentation Redoc |
| http://127.0.0.1:8003/admin/ | Administration Django |

## Comptes de démonstration

| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Administrateur | admin | admin123 |
| Agent | agent1 | agent123 |
| Client | client1 | client123 |
| Client | client2 | client123 |

## Modules API

### 01 — Authentification & Profils
- `POST /api/auth/register/` — Inscription client
- `POST /api/auth/login/` — Connexion JWT
- `POST /api/auth/refresh/` — Rafraîchir le token
- `GET/PATCH /api/auth/me/` — Profil utilisateur
- `POST /api/auth/change-password/` — Changer mot de passe
- `GET /api/auth/users/` — Liste utilisateurs (admin)
- `POST /api/auth/users/create/` — Créer un utilisateur (admin)

### 02 — Microcrédits
- `GET/POST /api/credits/` — Liste / créer une demande
- `GET /api/credits/{id}/` — Détail d'une demande
- `PATCH /api/credits/{id}/status/` — Changer le statut (agent/admin)
- `GET /api/credits/{id}/eligibility-score/` — Score d'éligibilité
- `GET /api/credits/{id}/schedule/` — Échéancier de remboursement
- `POST /api/credits/{id}/documents/` — Upload pièce justificative

### 03 — Remboursements
- `GET/POST /api/repayments/` — Liste / enregistrer un paiement
- `GET /api/repayments/schedules/` — Échéances
- `GET /api/repayments/credit/{id}/` — Historique par crédit
- `POST /api/repayments/process-alerts/` — Traiter alertes J-3/J+1

### 04 — Assurance mobile
- `GET /api/insurance/products/` — Catalogue produits
- `GET/POST /api/insurance/subscriptions/` — Souscriptions
- `GET /api/insurance/subscriptions/active/` — Polices actives
- `POST /api/insurance/process-alerts/` — Alertes expiration J-15

### 05 — Tableau de bord
- `GET /api/dashboard/stats/` — KPIs (admin)

### 06 — Notifications
- `GET /api/notifications/` — Mes notifications
- `GET /api/notifications/unread-count/` — Compteur non lues
- `PATCH /api/notifications/{id}/read/` — Marquer comme lue
- `POST /api/notifications/mark-all-read/` — Tout marquer lu

### 07 — Chat temps réel
- `GET/POST /api/chat/conversations/` — Conversations
- `GET /api/chat/conversations/{id}/` — Détail conversation
- `POST /api/chat/conversations/{id}/assign/` — Assigner un agent
- `POST /api/chat/conversations/{id}/close/` — Fermer
- `GET/POST /api/chat/conversations/{id}/messages/` — Messages REST
- `WS /ws/chat/{id}/?token=JWT` — WebSocket temps réel

## Interfaces

Le projet propose **3 interfaces distinctes** accessibles après connexion :

- **Client** : dashboard, crédits (création, suivi), assurances (catalogue, souscription), remboursements (échéancier), chat support, notifications, profil
- **Agent** : dashboard (statistiques, activités), crédits (gestion, approbation/rejet), chat support (conversations), notifications, profil
- **Admin** : dashboard (KPIs globaux), crédits (supervision), utilisateurs (gestion), chat (supervision), assurances (toutes souscriptions), notifications, profil

## Configuration PostgreSQL

```bash
# Variables d'environnement
set DB_ENGINE=django.db.backends.postgresql
set DB_NAME=cofinance
set DB_USER=postgres
set DB_PASSWORD=votre_mot_de_passe
set DB_HOST=localhost
set DB_PORT=5432
```

## Workflow crédit

```
Soumise → En analyse → Approuvée → Décaissée
                ↘ Rejetée
```

## Structure du projet

```
cofinance-platform/
├── config/           # Configuration Django
├── accounts/         # Auth JWT, profils, rôles
├── credits/          # Demandes de microcrédit
├── repayments/       # Remboursements et échéances
├── insurance/        # Produits et souscriptions
├── notifications/    # Alertes in-app
├── dashboard/        # Tableau de bord admin
├── chat/             # Support client WebSocket
├── templates/
│   ├── app/          # Interfaces graphiques (client, agent, admin)
│   │   ├── base.html # Layout principal avec sidebar
│   │   ├── login.html
│   │   ├── client/   # 7 pages
│   │   ├── agent/    # 6 pages
│   │   └── admin/    # 7 pages
│   └── chat/         # Pages chat historiques
└── requirements.txt
```

## Licence

Projet académique — Module Programmation Python.
