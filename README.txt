wsl


python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt


FRONTEND
cd frontend
npm run dev


BACKEND
uvicorn app.main:app --reload