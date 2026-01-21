# User Management System

Ein vollständiges Nutzerverwaltungssystem mit FastAPI (Backend) und SvelteKit (Frontend).

## Features

- Benutzerregistrierung mit Validierung
- Login/Logout mit Session-Management und JWT-Tokens
- Profilansicht und -bearbeitung
- Admin-Panel mit Nutzerverwaltung (aktivieren/deaktivieren/löschen)
- Passwort zurücksetzen via E-Mail (Resend)
- Two-Factor-Authentifizierung (TOTP)
- Zwei Benutzerrollen: Admin und User

## Tech Stack

### Backend
- **FastAPI**: Python Web Framework
- **PostgreSQL**: Datenbank
- **SQLAlchemy**: ORM
- **Resend**: E-Mail-Versand
- **PyOTP**: 2FA-Implementierung
- **JWT**: Token-basierte Authentifizierung

### Frontend
- **SvelteKit**: Frontend Framework
- **Tailwind CSS**: Styling
- **Vite**: Build Tool

## Projektstruktur

```
ai-user-administration/
├── backend/                  # FastAPI Backend
│   ├── routers/             # API Endpoints
│   │   ├── auth.py          # Authentifizierung
│   │   ├── users.py         # Benutzerprofil
│   │   ├── admin.py         # Admin-Funktionen
│   │   └── two_factor.py    # 2FA
│   ├── config.py            # Konfiguration
│   ├── database.py          # Datenbankverbindung
│   ├── models.py            # SQLAlchemy Models
│   ├── schemas.py           # Pydantic Schemas
│   ├── security.py          # Authentifizierungslogik
│   ├── email_service.py     # E-Mail-Funktionen
│   ├── two_factor.py        # 2FA-Logik
│   ├── main.py              # Hauptanwendung
│   └── requirements.txt     # Python Dependencies
│
├── frontend/                # SvelteKit Frontend
│   ├── src/
│   │   ├── lib/
│   │   │   └── api.js       # API Client
│   │   ├── routes/          # Seiten
│   │   │   ├── +layout.svelte
│   │   │   ├── +page.svelte
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── profile/
│   │   │   ├── admin/
│   │   │   ├── forgot-password/
│   │   │   └── reset-password/
│   │   ├── app.html
│   │   └── app.css          # Tailwind CSS
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── README.md
```

## Installation & Setup

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

#### PostgreSQL Datenbank erstellen

```bash
# PostgreSQL starten
brew services start postgresql  # macOS
# oder
sudo systemctl start postgresql  # Linux

# Datenbank erstellen
createdb user_management

# Alternativ via psql:
psql postgres
CREATE DATABASE user_management;
\q
```

#### Python Virtual Environment

```bash
cd backend
python -m venv venv

# Aktivieren
source venv/bin/activate  # macOS/Linux
# oder
venv\Scripts\activate  # Windows
```

#### Dependencies installieren

```bash
pip install -r requirements.txt
```

#### Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Bearbeite `.env` und setze folgende Werte:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/user_management

# Security (generiere einen sicheren Schlüssel)
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Resend)
RESEND_API_KEY=re_your_resend_api_key
FROM_EMAIL=noreply@yourdomain.com

# Application
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Admin user (wird beim ersten Start erstellt)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=changeme123
```

**Secret Key generieren:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Backend starten

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Das Backend läuft nun auf: `http://localhost:8000`
API-Dokumentation: `http://localhost:8000/docs`

### 3. Frontend Setup

Öffne ein neues Terminal:

```bash
cd frontend
```

#### Dependencies installieren

```bash
npm install
```

#### Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Bearbeite `.env`:

```env
PUBLIC_API_URL=http://localhost:8000
```

#### Frontend starten

```bash
npm run dev
```

Das Frontend läuft nun auf: `http://localhost:5173`

## Verwendung

### 1. Admin-Login

Beim ersten Start wird automatisch ein Admin-Benutzer mit den Daten aus der `.env` erstellt:

- **E-Mail**: `admin@example.com` (oder deine konfigurierte E-Mail)
- **Passwort**: `changeme123` (oder dein konfiguriertes Passwort)

**Wichtig**: Ändere das Admin-Passwort nach dem ersten Login!

### 2. Neue Benutzer registrieren

1. Gehe zu `http://localhost:5173/register`
2. Fülle das Registrierungsformular aus
3. Du erhältst eine Willkommens-E-Mail (wenn Resend konfiguriert ist)
4. Melde dich mit deinen Zugangsdaten an

### 3. Profil verwalten

Nach dem Login kannst du:

- Deinen Namen ändern
- Dein Passwort ändern
- 2FA aktivieren/deaktivieren

### 4. Admin-Panel

Als Admin hast du Zugriff auf:

- Liste aller Benutzer
- Benutzer aktivieren/deaktivieren
- Admin-Rechte vergeben/entziehen
- Benutzer löschen

### 5. Passwort zurücksetzen

1. Klicke auf "Passwort vergessen?" beim Login
2. Gib deine E-Mail-Adresse ein
3. Du erhältst eine E-Mail mit einem Reset-Link
4. Setze ein neues Passwort

### 6. Two-Factor-Authentication (2FA)

1. Gehe zu deinem Profil
2. Klicke auf "2FA einrichten"
3. Scanne den QR-Code mit einer Authenticator-App (z.B. Google Authenticator, Authy)
4. Gib den Code aus der App ein, um 2FA zu aktivieren
5. Bei jedem Login musst du nun zusätzlich den 2FA-Code eingeben

## API-Endpunkte

### Authentifizierung

- `POST /api/auth/register` - Registrierung
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Aktueller Benutzer
- `POST /api/auth/password-reset-request` - Passwort-Reset anfordern
- `POST /api/auth/password-reset-confirm` - Passwort zurücksetzen

### Benutzer

- `GET /api/users/profile` - Profil abrufen
- `PUT /api/users/profile` - Profil aktualisieren

### Admin

- `GET /api/admin/users` - Alle Benutzer auflisten
- `GET /api/admin/users/{user_id}` - Benutzer abrufen
- `PATCH /api/admin/users/{user_id}` - Benutzer aktualisieren
- `DELETE /api/admin/users/{user_id}` - Benutzer löschen

### Two-Factor Authentication

- `POST /api/2fa/setup` - 2FA einrichten
- `POST /api/2fa/verify` - 2FA verifizieren
- `POST /api/2fa/disable` - 2FA deaktivieren

## Entwicklung

### Backend Tests ausführen

```bash
cd backend
pytest
```

### Frontend Build erstellen

```bash
cd frontend
npm run build
```

### Datenbank-Migrationen (Optional mit Alembic)

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Produktions-Deployment

### Backend

1. Setze `DEBUG=False` in der Konfiguration
2. Verwende einen Production ASGI Server (z.B. Gunicorn + Uvicorn)
3. Nutze HTTPS
4. Setze sichere CORS-Einstellungen
5. Verwende einen Secret Key Manager für sensible Daten

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend

```bash
npm run build
```

Das Build-Verzeichnis kann dann auf einem Static-Host (Vercel, Netlify, etc.) deployed werden.

### Umgebungsvariablen in Produktion

- Nutze keine `.env`-Dateien
- Verwende Secret Manager (AWS Secrets Manager, Azure Key Vault, etc.)
- Setze Environment Variables über dein Hosting-System

## Sicherheit

### Best Practices

- **Passwörter**: Werden mit bcrypt gehasht
- **JWT Tokens**: Signiert mit HS256
- **Session Management**: Token-basiert mit Ablaufzeit
- **2FA**: TOTP-basiert (RFC 6238)
- **CORS**: Konfiguriert für Frontend-Domain
- **SQL Injection**: Geschützt durch SQLAlchemy ORM
- **E-Mail Validierung**: Pydantic EmailStr

### Empfohlene Maßnahmen für Produktion

- Rate Limiting implementieren
- HTTPS erzwingen
- Content Security Policy (CSP) Headers setzen
- Regelmäßige Security Updates
- Logging und Monitoring einrichten
- Backup-Strategie für Datenbank

## Troubleshooting

### Backend startet nicht

**Problem**: Datenbank-Verbindungsfehler

```bash
# Prüfe PostgreSQL Status
pg_isready
# oder
brew services list  # macOS

# Prüfe DATABASE_URL in .env
echo $DATABASE_URL
```

**Problem**: Import-Fehler oder bcrypt-Fehler

```bash
# Aktiviere Virtual Environment
source venv/bin/activate

# Entferne alte Versionen (falls vorhanden)
pip uninstall -y bcrypt passlib

# Installiere Dependencies neu
pip install -r requirements.txt
```

### Frontend startet nicht

**Problem**: Node Module fehlen

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Tailwind CSS funktioniert nicht

```bash
# Prüfe ob PostCSS und Tailwind installiert sind
npm list tailwindcss postcss autoprefixer
```

### E-Mail wird nicht versendet

**Problem**: Resend API Key ungültig

1. Prüfe `RESEND_API_KEY` in der `.env`
2. Verifiziere deine Domain bei Resend
3. Prüfe die FROM_EMAIL - sie muss von einer verifizierten Domain sein

### 2FA funktioniert nicht

**Problem**: Codes werden nicht akzeptiert

1. Stelle sicher, dass die Systemzeit korrekt ist (TOTP ist zeitbasiert)
2. Nutze `valid_window=1` in der `verify_2fa_code` Funktion (bereits implementiert)

## Lizenz

MIT

## Support

Bei Fragen oder Problemen öffne ein Issue im Repository.
