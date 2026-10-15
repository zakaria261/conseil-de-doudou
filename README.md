# Les Conseils de Doudou

Première version web responsive du projet, avec une interface Angular et une API Python FastAPI.

## Lancer l’application

Ouvre deux terminaux depuis le dossier du projet.

Dans le premier, démarre l’API :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --reload-exclude ".venv/**" --port 8000
```

Dans le second, démarre l’interface :

```bash
cd frontend
npm install
npm start
```

Ouvre ensuite [http://localhost:4200](http://localhost:4200). L’interface transmet les appels `/api` au serveur Python sur le port 8000. La documentation de l’API est disponible sur [http://localhost:8000/docs](http://localhost:8000/docs).

## Contenu de la démonstration

- Accueil responsive donnant directement accès à quatre fiches d’accompagnateurs : portrait, parcours, compétences et prochain créneau.
- Recherche par prénom ou sujet et bouton « + » pour suivre un profil, avec enregistrement du suivi dans la base de démonstration.
- Espace accompagnateur pour gérer une présentation, la visibilité et des créneaux.
- Réservation d’une séance par messages ou en visioconférence.
- Rendez-vous, messagerie, partage public ou dans un cercle privé de démonstration.
- Profil modifiable, notifications d’encouragement et six offres tarifaires.
- Espace d’administration pour masquer des profils, ajuster les prix et retirer des publications.
- Confirmation avant l’appel au 3114.

Les profils, portraits, parcours, messages et publications préchargés sont fictifs. Les qualifications et disponibilités devront être vérifiées avant d’ouvrir le service. L’API crée `backend/doudou.db` au premier démarrage.

## État du prototype

Cette base sert à présenter les parcours et à valider l’interface. Elle ne doit pas recevoir de conversations ou de données personnelles réelles. Elle ne comprend pas encore de comptes utilisateurs, d’authentification réelle, de stockage chiffré, de paiement, de visioconférence intégrée ni de notifications push. Les échanges de démonstration sont stockés dans une base SQLite locale.

Avant une mise en service, il reste à définir et mettre en œuvre les critères d’admission, les règles de modération, les conditions d’abonnement et la durée d’engagement, la gestion des droits d’accès et de suppression des données, ainsi que la sécurité des conversations. Le jeton d’administration `demo-admin` est uniquement destiné à cette démonstration locale.
