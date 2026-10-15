"""API locale de démonstration des Conseils de Doudou.

Les données semées sont fictives. Cette API n'implémente pas encore de comptes,
d'authentification utilisateur ni de chiffrement de bout en bout.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


DB_PATH = Path(__file__).with_name("doudou.db")
ADMIN_TOKEN = os.getenv("DOUDOU_ADMIN_TOKEN", "demo-admin")

app = FastAPI(
    title="Les Conseils de Doudou API",
    description="API de démonstration pour l'écoute, les rendez-vous et la communauté.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_data(db: sqlite3.Connection) -> None:
    if db.execute("SELECT COUNT(*) FROM coaches").fetchone()[0] == 0:
        coaches = [
            ("hugo", "Hugo", "HU", "Accompagnateur de vie", "Licence en psychologie · Sorbonne · Formation en psychologie légale", "Je m’appelle Hugo. J’ai étudié la psychologie à la Sorbonne, puis suivi une formation en psychologie légale. Je propose une écoute attentive et sans jugement.", ["Écoute", "Relations", "Confiance en soi"], ["Samedi 14:00", "Mardi 19:00"], 1),
            ("julie", "Julie", "JU", "Accompagnatrice de vie", "Licence en psychologie · Université Paul-Valéry · Spécialisation en psychologie du travail", "Je m’appelle Julie. Après ma licence en psychologie à l’université Paul-Valéry, je me suis spécialisée dans les questions liées au travail. Ici, tu peux parler librement de ce qui te préoccupe.", ["Vie professionnelle", "Relations", "Stress du quotidien"], ["Vendredi 16:00", "Lundi 09:30", "Mercredi 18:00"], 1),
            ("sarah", "Sarah", "SA", "Accompagnatrice de vie", "Licence en sciences de l’éducation · Université Toulouse Jean-Jaurès · Ingénierie de la formation", "Je m’appelle Sarah. J’ai étudié les sciences de l’éducation à Toulouse Jean-Jaurès et l’accompagnement pédagogique. J’aime aider à retrouver de la clarté dans les périodes de transition.", ["Confiance en soi", "Transitions", "Organisation"], ["Samedi 10:30", "Lundi 17:00", "Mardi 12:30"], 1),
            ("thomas", "Thomas", "TH", "Accompagnateur de vie", "Licence en psychologie · Université de Nîmes · Formation en psychologie clinique", "Je m’appelle Thomas. Après une licence en psychologie à Nîmes, j’ai suivi une formation en psychologie clinique et en accompagnement des personnes. On avance par petites étapes, à ton rythme.", ["Changements de vie", "Motivation", "Émotions"], ["Lundi 11:00", "Jeudi 17:30"], 1),
        ]
        db.executemany(
            """INSERT INTO coaches (id,name,initials,title,studies,bio,specialties,next_slots,active)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            [(i, n, ini, title, studies, bio, json.dumps(skills, ensure_ascii=False), json.dumps(slots, ensure_ascii=False), active) for i, n, ini, title, studies, bio, skills, slots, active in coaches],
        )
        db.execute("INSERT INTO coach_follows (coach_id,actor) VALUES (?,?)", ("sarah", "Dounia"))

    if db.execute("SELECT COUNT(*) FROM offers").fetchone()[0] == 0:
        offers = [
            ("community", "Communauté", "Accès à Chat & partage et aux notifications, avec publicités.", 0.0, "gratuit", 0, 1),
            ("message", "Une heure par messages", "Un échange individuel écrit, à ton rythme.", 13.99, "la séance", 0, 1),
            ("video", "Une heure en visio", "Un temps de parole en visioconférence.", 14.99, "la séance", 0, 1),
            ("chat", "Chat illimité", "Des échanges réguliers par messages avec une accompagnatrice.", 24.99, "/ mois", 0, 1),
            ("four-visio", "Chat + 4 visios", "Chat illimité et quatre visioconférences chaque mois.", 33.99, "/ mois", 1, 1),
            ("all-visio", "Chat + visios illimités", "Chat et visioconférences sans limite mensuelle.", 49.99, "/ mois", 0, 1),
        ]
        db.executemany("INSERT INTO offers VALUES (?,?,?,?,?,?,?)", offers)

    if db.execute("SELECT COUNT(*) FROM posts").fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        posts = [
            ("Lina", "LI", now, "J’apprends à dire non, doucement", "J’ai réussi à décliner une sortie ce week-end sans inventer d’excuse. Ce n’est pas grand-chose, mais je suis fière de m’être écoutée.", "Confiance en soi", "Tout le monde", 12, 4, 0),
            ("Maya", "MA", now, "Les petits rituels qui font du bien", "En ce moment, je note chaque soir une chose que j’ai faite pour moi. Même les jours compliqués, il y en a toujours une.", "Vie quotidienne", "Cercle confiance en soi", 8, 3, 1),
            ("Camille", "CA", now, "Comment traverser une période de changement ?", "Je change de travail le mois prochain et je suis partagée entre impatience et peur. Si vous avez vécu une transition similaire, je vous lis.", "Travail", "Tout le monde", 16, 7, 0),
        ]
        db.executemany("""INSERT INTO posts (author,initials,created_at,title,body,topic,room,likes,replies,is_private)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""", posts)

    if db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] == 0:
        db.execute("INSERT INTO bookings (coach_id,coach_name,coach_initials,kind,date_time,status) VALUES (?,?,?,?,?,?)", ("sarah", "Sarah", "SA", "Séance par messages · 1 h", "Samedi 17 octobre · 10:30", "Confirmé"))

    if db.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0:
        samples = [
            ("Sarah", "Dounia", "Bonjour Dounia, contente de te retrouver ici. Comment tu te sens aujourd’hui ?", "10:32"),
            ("Dounia", "Sarah", "Un peu fatiguée, mais j’avais envie de parler de cette semaine.", "10:39"),
            ("Sarah", "Dounia", "On prend le temps, à ton rythme. Qu’est-ce qui te ferait du bien de déposer ?", "10:42"),
            ("Julie", "Dounia", "Merci pour ta confiance. On pourra reprendre cette question lors de notre prochain échange.", "Hier"),
            ("Maya", "Cercle confiance", "J’ai pris dix minutes pour moi avant de commencer la journée.", "Mar."),
        ]
        db.executemany("INSERT INTO messages (sender,recipient,text,time_label) VALUES (?,?,?,?)", samples)

    if db.execute("SELECT COUNT(*) FROM profile").fetchone()[0] == 0:
        db.execute("INSERT INTO profile (id,pseudo,bio,email) VALUES (1,?,?,?)", ("Dounia", "J’avance à mon rythme, un jour après l’autre.", "dounia@exemple.fr"))


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS coaches (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, initials TEXT NOT NULL,
                title TEXT NOT NULL, studies TEXT NOT NULL, bio TEXT NOT NULL,
                specialties TEXT NOT NULL, next_slots TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS coach_follows (
                coach_id TEXT NOT NULL, actor TEXT NOT NULL,
                PRIMARY KEY (coach_id, actor)
            );
            CREATE TABLE IF NOT EXISTS offers (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL,
                price REAL NOT NULL, unit TEXT NOT NULL, popular INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT NOT NULL, initials TEXT NOT NULL,
                created_at TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL, topic TEXT NOT NULL,
                room TEXT NOT NULL, likes INTEGER NOT NULL DEFAULT 0, replies INTEGER NOT NULL DEFAULT 0,
                is_private INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS post_reactions (
                post_id INTEGER NOT NULL, actor TEXT NOT NULL,
                PRIMARY KEY (post_id, actor)
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT, coach_id TEXT NOT NULL, coach_name TEXT NOT NULL,
                coach_initials TEXT NOT NULL, kind TEXT NOT NULL, date_time TEXT NOT NULL, status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, recipient TEXT NOT NULL,
                text TEXT NOT NULL, time_label TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY, pseudo TEXT NOT NULL, bio TEXT NOT NULL, email TEXT NOT NULL
            );
            """
        )
        seed_data(db)


init_db()


class BookingInput(BaseModel):
    coach_id: str
    offer_id: str
    date_time: str
    kind: str


class PostInput(BaseModel):
    author: str = "Dounia"
    initials: str = "DO"
    body: str = Field(min_length=1, max_length=600)
    title: str = Field(min_length=1, max_length=100)
    topic: str = "Vie quotidienne"
    room: str = "Tout le monde"
    is_private: bool = False


class MessageInput(BaseModel):
    recipient: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=2000)


class LikeInput(BaseModel):
    liked: bool


class FollowInput(BaseModel):
    followed: bool


class ProfileInput(BaseModel):
    pseudo: str = Field(min_length=1, max_length=32)
    bio: str = Field(default="", max_length=240)
    email: str = Field(default="", max_length=250)


class CompanionProfileInput(BaseModel):
    bio: str = Field(min_length=1, max_length=400)
    next_slots: list[str] = Field(max_length=12)
    active: bool = True


class AdminPatch(BaseModel):
    active: bool | None = None
    price: float | None = Field(default=None, ge=0, le=10000)


def require_admin(x_admin_token: str = Header(default="")) -> None:
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Accès réservé à l’administration.")


def coach_dict(row: sqlite3.Row) -> dict[str, Any]:
    ages = {"hugo": 23, "julie": 29, "sarah": 26, "thomas": 34}
    return {
        "id": row["id"], "name": row["name"], "initials": row["initials"],
        "age": ages.get(row["id"]), "photoUrl": f"portraits/{row['id']}.webp",
        "title": row["title"], "studies": row["studies"], "bio": row["bio"],
        "specialties": json.loads(row["specialties"]), "nextSlots": json.loads(row["next_slots"]),
        "online": bool(row["active"]), "followed": bool(row["followed"]) if "followed" in row.keys() else False,
    }


def offer_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {"id": row["id"], "name": row["name"], "description": row["description"], "price": row["price"], "unit": row["unit"], "popular": bool(row["popular"]), "active": bool(row["active"])}


def post_dict(row: sqlite3.Row) -> dict[str, Any]:
    keys = row.keys()
    return {"id": row["id"], "author": row["author"], "initials": row["initials"], "time": "À l’instant", "title": row["title"], "body": row["body"], "topic": row["topic"], "room": row["room"], "likes": row["likes"], "replies": row["replies"], "private": bool(row["is_private"]), "liked": bool(row["liked"]) if "liked" in keys else False}


def booking_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"], "coachName": row["coach_name"], "coachInitials": row["coach_initials"],
        "kind": row["kind"], "dateTime": row["date_time"], "status": row["status"],
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "demonstration"}


@app.get("/api/coaches")
def list_coaches() -> list[dict[str, Any]]:
    with connect() as db:
        return [coach_dict(row) for row in db.execute(
            """SELECT coaches.*, EXISTS(SELECT 1 FROM coach_follows
               WHERE coach_follows.coach_id=coaches.id AND coach_follows.actor='Dounia') AS followed
               FROM coaches ORDER BY name"""
        )]


@app.post("/api/coaches/{coach_id}/follow")
def follow_coach(coach_id: str, payload: FollowInput) -> dict[str, bool]:
    # Suivi local du profil fictif Dounia dans cette démonstration mono-utilisateur.
    with connect() as db:
        if not db.execute("SELECT 1 FROM coaches WHERE id=?", (coach_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Profil introuvable.")
        if payload.followed:
            db.execute("INSERT OR IGNORE INTO coach_follows (coach_id,actor) VALUES (?,?)", (coach_id, "Dounia"))
        else:
            db.execute("DELETE FROM coach_follows WHERE coach_id=? AND actor=?", (coach_id, "Dounia"))
    return {"followed": payload.followed}


@app.get("/api/offers")
def list_offers() -> list[dict[str, Any]]:
    with connect() as db:
        return [offer_dict(row) for row in db.execute("SELECT * FROM offers ORDER BY price")]


@app.get("/api/posts")
def list_posts() -> list[dict[str, Any]]:
    with connect() as db:
        return [post_dict(row) for row in db.execute(
            """SELECT posts.*, EXISTS(SELECT 1 FROM post_reactions
               WHERE post_reactions.post_id=posts.id AND post_reactions.actor='Dounia') AS liked
               FROM posts ORDER BY id DESC"""
        )]


@app.post("/api/posts")
def create_post(payload: PostInput) -> dict[str, Any]:
    room = "Cercle confiance en soi" if payload.is_private else "Tout le monde"
    with connect() as db:
        cursor = db.execute(
            """INSERT INTO posts (author,initials,created_at,title,body,topic,room,likes,replies,is_private)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (payload.author, payload.initials, datetime.now(timezone.utc).isoformat(), payload.title, payload.body, payload.topic, room, 0, 0, int(payload.is_private)),
        )
        row = db.execute("SELECT * FROM posts WHERE id=?", (cursor.lastrowid,)).fetchone()
        return post_dict(row)


@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int, payload: LikeInput) -> dict[str, int]:
    # L'interface est une démo mono-utilisateur ; la vraie identité viendra du système de comptes.
    with connect() as db:
        exists = db.execute("SELECT id FROM posts WHERE id=?", (post_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Partage introuvable.")
        if payload.liked:
            inserted = db.execute("INSERT OR IGNORE INTO post_reactions (post_id,actor) VALUES (?,?)", (post_id, "Dounia")).rowcount
            if inserted:
                db.execute("UPDATE posts SET likes=likes+1 WHERE id=?", (post_id,))
        else:
            removed = db.execute("DELETE FROM post_reactions WHERE post_id=? AND actor=?", (post_id, "Dounia")).rowcount
            if removed:
                db.execute("UPDATE posts SET likes=MAX(0,likes-1) WHERE id=?", (post_id,))
        return {"likes": db.execute("SELECT likes FROM posts WHERE id=?", (post_id,)).fetchone()[0]}


@app.get("/api/bookings")
def list_bookings() -> list[dict[str, Any]]:
    with connect() as db:
        return [booking_dict(row) for row in db.execute("SELECT * FROM bookings ORDER BY id DESC")]


@app.post("/api/bookings")
def create_booking(payload: BookingInput) -> dict[str, Any]:
    with connect() as db:
        coach = db.execute("SELECT * FROM coaches WHERE id=? AND active=1", (payload.coach_id,)).fetchone()
        if not coach:
            raise HTTPException(status_code=404, detail="Ce profil n’est plus disponible.")
        cursor = db.execute(
            "INSERT INTO bookings (coach_id,coach_name,coach_initials,kind,date_time,status) VALUES (?,?,?,?,?,?)",
            (coach["id"], coach["name"], coach["initials"], payload.kind, payload.date_time, "Confirmé"),
        )
        return booking_dict(db.execute("SELECT * FROM bookings WHERE id=?", (cursor.lastrowid,)).fetchone())


@app.get("/api/messages")
def list_messages() -> dict[str, list[dict[str, Any]]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM messages ORDER BY id").fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        thread = row["sender"] if row["recipient"] == "Dounia" else row["recipient"]
        grouped.setdefault(thread, []).append({
            "sender": row["sender"], "text": row["text"], "time": row["time_label"],
            "own": row["sender"] == "Dounia",
        })
    return grouped


@app.post("/api/messages")
def create_message(payload: MessageInput) -> dict[str, Any]:
    with connect() as db:
        profile = db.execute("SELECT pseudo FROM profile WHERE id=1").fetchone()
        sender = profile["pseudo"] if profile else "Dounia"
        time_label = datetime.now().strftime("%H:%M")
        cursor = db.execute("INSERT INTO messages (sender,recipient,text,time_label) VALUES (?,?,?,?)", (sender, payload.recipient, payload.text, time_label))
        row = db.execute("SELECT * FROM messages WHERE id=?", (cursor.lastrowid,)).fetchone()
        return {"sender": row["sender"], "text": row["text"], "time": row["time_label"], "own": True}


@app.get("/api/profile")
def get_profile() -> dict[str, str]:
    with connect() as db:
        row = db.execute("SELECT pseudo,bio,email FROM profile WHERE id=1").fetchone()
        return dict(row)


@app.put("/api/profile")
def update_profile(payload: ProfileInput) -> dict[str, str]:
    with connect() as db:
        db.execute("UPDATE profile SET pseudo=?,bio=?,email=? WHERE id=1", (payload.pseudo, payload.bio, payload.email))
        return dict(db.execute("SELECT pseudo,bio,email FROM profile WHERE id=1").fetchone())


@app.get("/api/companion/profile")
def get_companion_profile() -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT * FROM coaches WHERE id='sarah'").fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Profil d’exemple introuvable.")
        return coach_dict(row)


@app.put("/api/companion/profile")
def update_companion_profile(payload: CompanionProfileInput) -> dict[str, Any]:
    clean_slots = [slot.strip() for slot in payload.next_slots if slot.strip()]
    if any(len(slot) > 40 for slot in clean_slots):
        raise HTTPException(status_code=422, detail="Un créneau ne peut pas dépasser 40 caractères.")
    with connect() as db:
        db.execute(
            "UPDATE coaches SET bio=?,next_slots=?,active=? WHERE id='sarah'",
            (payload.bio.strip(), json.dumps(clean_slots, ensure_ascii=False), int(payload.active)),
        )
        row = db.execute("SELECT * FROM coaches WHERE id='sarah'").fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Profil d’exemple introuvable.")
        return coach_dict(row)


@app.patch("/api/admin/coaches/{coach_id}", dependencies=[Depends(require_admin)])
def update_coach(coach_id: str, payload: AdminPatch) -> dict[str, bool]:
    if payload.active is None:
        raise HTTPException(status_code=400, detail="Aucun changement fourni.")
    with connect() as db:
        cursor = db.execute("UPDATE coaches SET active=? WHERE id=?", (int(payload.active), coach_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Profil introuvable.")
    return {"active": payload.active}


@app.patch("/api/admin/offers/{offer_id}", dependencies=[Depends(require_admin)])
def update_offer(offer_id: str, payload: AdminPatch) -> dict[str, Any]:
    if payload.active is None and payload.price is None:
        raise HTTPException(status_code=400, detail="Aucun changement fourni.")
    with connect() as db:
        row = db.execute("SELECT * FROM offers WHERE id=?", (offer_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Formule introuvable.")
        db.execute("UPDATE offers SET active=?,price=? WHERE id=?", (int(payload.active) if payload.active is not None else row["active"], payload.price if payload.price is not None else row["price"], offer_id))
        updated = db.execute("SELECT * FROM offers WHERE id=?", (offer_id,)).fetchone()
        return offer_dict(updated)


@app.delete("/api/admin/posts/{post_id}", dependencies=[Depends(require_admin)])
def delete_post(post_id: int) -> dict[str, bool]:
    with connect() as db:
        cursor = db.execute("DELETE FROM posts WHERE id=?", (post_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Partage introuvable.")
    return {"deleted": True}
