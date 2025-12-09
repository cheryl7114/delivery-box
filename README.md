# Delivery Box

A full-stack contactless delivery box application with React frontend and Flask backend.

## Setup

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`

### Backend Setup

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Install dependencies (if needed):
```bash
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python backend/app.py
```

The backend will run on `http://localhost:5000`

## Development

- Frontend development server: `http://localhost:5173`
- Backend API server: `http://localhost:5000`
- The frontend is configured to proxy API requests to the backend

