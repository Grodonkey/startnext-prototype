# User Management System

Ein vollständiges Nutzerverwaltungssystem mit FastAPI (Backend) und SvelteKit (Frontend).

## Features

- Benutzerregistrierung mit Validierung
- Login/Logout mit Session-Management und JWT-Tokens
- Profilansicht und -bearbeitung
- Admin-Panel mit Nutzerverwaltung
- Passwort zurücksetzen via E-Mail (Resend)
- Two-Factor-Authentifizierung (TOTP)
- Email-Test-Tool für Admins
- Zwei Benutzerrollen: Admin und User

## Tech Stack

**Backend:**
- FastAPI + Python
- PostgreSQL + SQLAlchemy
- JWT + bcrypt
- Resend (Email)
- PyOTP (2FA)

**Frontend:**
- SvelteKit
- Tailwind CSS
- Vite

## Schnellstart

### Voraussetzungen

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Resend Account (für E-Mail-Versand)

### 1. Repository klonen

```bash
git clone <repository-url>
cd ai-user-administration
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Datenbank erstellen
createdb user_management

# .env konfigurieren
cp .env.example .env
# Bearbeite .env und setze Werte

# Backend starten
uvicorn main:app --reload
```

Backend läuft auf: `http://localhost:8000`

**Siehe [backend/BACKEND.md](backend/BACKEND.md) für Details**

### 3. Frontend Setup

```bash
cd frontend
npm install

# .env konfigurieren
cp .env.example .env
# Bearbeite .env (normalerweise keine Änderung nötig)

# Frontend starten
npm run dev
```

Frontend läuft auf: `http://localhost:5173`

**Siehe [frontend/FRONTEND.md](frontend/FRONTEND.md) für Details**

## Verwendung

### Erster Admin-Login

Der Admin-User wird automatisch beim ersten Backend-Start erstellt:

- **E-Mail**: Aus `ADMIN_EMAIL` in `.env`
- **Passwort**: Aus `ADMIN_PASSWORD` in `.env`

**Wichtig**: Ändere das Admin-Passwort nach dem ersten Login!

### Als normaler Benutzer

1. Gehe zu `http://localhost:5173/register`
2. Erstelle einen Account
3. Melde dich an
4. Verwalte dein Profil und aktiviere optional 2FA

### Als Admin

1. Melde dich an
2. Gehe zum Admin-Panel
3. Verwalte Benutzer (aktivieren/deaktivieren, Admin-Rechte, löschen)
4. Teste Emails über Email-Test

## Dokumentation

- **[Backend Dokumentation](backend/BACKEND.md)** - FastAPI, Datenbank, API-Endpunkte
- **[Frontend Dokumentation](frontend/FRONTEND.md)** - SvelteKit, Routing, Deployment
- **[FAQ](FAQ.md)** - Häufig gestellte Fragen

## Projektstruktur

```
ai-user-administration/
├── backend/                    # FastAPI Backend
│   ├── routers/               # API Endpoints
│   ├── models.py              # Datenbankmodelle
│   ├── schemas.py             # API Schemas
│   ├── security.py            # Authentifizierung
│   ├── email_service.py       # E-Mail-Versand
│   ├── two_factor.py          # 2FA-Logik
│   ├── main.py                # Hauptanwendung
│   ├── requirements.txt       # Python Dependencies
│   └── BACKEND.md             # Backend-Dokumentation
│
├── frontend/                  # SvelteKit Frontend
│   ├── src/
│   │   ├── lib/api.js        # API Client
│   │   └── routes/           # Seiten
│   ├── package.json          # Node Dependencies
│   └── FRONTEND.md           # Frontend-Dokumentation
│
├── README.md                  # Diese Datei
└── FAQ.md                     # Häufig gestellte Fragen
```

## API-Endpunkte

Vollständige API-Dokumentation: `http://localhost:8000/docs`

### Wichtigste Endpunkte:

- `POST /api/auth/register` - Registrierung
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/users/profile` - Profil abrufen
- `PUT /api/users/profile` - Profil aktualisieren
- `GET /api/admin/users` - Benutzer auflisten (Admin)
- `POST /api/admin/test-email` - Test-Email senden (Admin)
- `POST /api/2fa/setup` - 2FA einrichten
- `POST /api/2fa/verify` - 2FA aktivieren

## Sicherheit

- **Passwörter**: Mit bcrypt gehasht
- **JWT Tokens**: Signiert mit SECRET_KEY (HS256)
- **2FA**: TOTP-basiert (RFC 6238)
- **CORS**: Konfiguriert für Frontend-Domain
- **SQL Injection**: Geschützt durch SQLAlchemy ORM

**Siehe [FAQ.md](FAQ.md#sicherheit) für Details zum SECRET_KEY**

## Häufige Fragen

### Muss ich das Backend neu bauen bei .env-Änderungen?

**Nein**, nur neu starten. Siehe [FAQ.md](FAQ.md#installation--setup)

### Wofür ist der SECRET_KEY?

Signiert JWT-Tokens. Siehe [FAQ.md](FAQ.md#sicherheit)

### Wie teste ich Email-Versand?

Admin → Email-Test. Siehe [FAQ.md](FAQ.md#emails)

**Weitere Fragen:** [FAQ.md](FAQ.md)

## Deployment

### Production Checklist

- [ ] Sicheren `SECRET_KEY` generieren (32+ Zeichen)
- [ ] PostgreSQL Managed Database nutzen
- [ ] HTTPS aktivieren
- [ ] Environment Variables über Secret Manager
- [ ] Rate Limiting implementieren
- [ ] Logging und Monitoring einrichten
- [ ] Backup-Strategie für Datenbank

**Siehe:**
- [Backend Deployment](backend/BACKEND.md#produktions-deployment)
- [Frontend Deployment](frontend/FRONTEND.md#deployment)

## Support

- **Backend-Probleme**: [backend/BACKEND.md](backend/BACKEND.md#troubleshooting)
- **Frontend-Probleme**: [frontend/FRONTEND.md](frontend/FRONTEND.md#troubleshooting)
- **Allgemeine Fragen**: [FAQ.md](FAQ.md)
- **Issues**: GitHub Issues erstellen

## Lizenz

MIT

## Credits

- **FastAPI**: https://fastapi.tiangolo.com
- **SvelteKit**: https://kit.svelte.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Resend**: https://resend.com
