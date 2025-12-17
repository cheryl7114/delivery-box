# Delivery Box

A smart parcel management system with server-side rendering using Flask, JavaScript, and Tailwind CSS.

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML + Vanilla JavaScript + Tailwind CSS
- **Database**: MySQL (XAMPP)
- **Authentication**: Google OAuth 2.0 + JWT
- **Styling**: Tailwind CSS (via CDN)

## Setup Instructions

### 1. Prerequisites

- Python 3.7+
- XAMPP MySQL running
- Google OAuth credentials

### 2. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

do: 

```bash
cp .env.example .env
```

then fill in your own credentials in your env file.

### 4. Run the Application

```bash
source venv/bin/activate
python app/app.py
```

The application will run on `http://localhost:5001`

## Database

The application uses MySQL with the following tables:
- `users` - User accounts
- `boxes` - Delivery boxes
- `parcels` - Parcel tracking

Initialize the database by running:
```bash
mysql -u root < db/schema.sql
```

## Notes

- No separate frontend build process needed
- All styling is handled by Tailwind CSS
- Google OAuth auto-creates users on first login
- JWT tokens expire after 7 days

