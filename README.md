# WSL + VS Code + Windows Repo Setup + Backend Setup

## 1. Keep the repo on Windows

Example Windows path:

```text
C:\Users\<username>\Desktop\NestScanner
```

The same folder is accessed from WSL as:

```text
/mnt/c/Users/<username>/Desktop/NestScanner
```

---

## 2. Open WSL and go to the repo

```bash
cd /mnt/c/Users/<username>/Desktop/NestScanner
```

---

## 3. Remove any old virtual environment

```bash
rm -rf .venv
```

---

## 4. Create a new WSL virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

You should now see:

```text
(.venv)
```

in the terminal prompt.

---

## 5. Install dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## 6. Verify the virtual environment

Check Python:

```bash
which python
```

It should point to:

```text
/mnt/c/Users/<username>/Desktop/NestScanner/.venv/bin/python
```

Check pip:

```bash
python -m pip --version
```

---

## 7. Open the repo in VS Code WSL mode

From the WSL terminal:

```bash
code .
```

Make sure the Microsoft **WSL extension** is installed in VS Code.

VS Code should show something like:

```text
WSL: Ubuntu
```

in the bottom-left.

---

## 8. Select the correct Python interpreter

In VS Code:

```text
Ctrl + Shift + P
```

Then choose:

```text
Python: Select Interpreter
```

Select:

```text
.venv/bin/python
```

or:

```text
/mnt/c/Users/<username>/Desktop/NestScanner/.venv/bin/python
```

If VS Code shows both:

```text
Global
Workspace
```

choose:

```text
Workspace
```

This means the NestScanner workspace will use this interpreter.

---

# Python backend

Go to the backend folder:

```bash
cd backend
```

Run FastAPI:

```bash
python -m uvicorn app.main:app --reload
```

---
# Frontend

The frontend uses **Node.js 22**. Run the following commands inside WSL.

```bash
# Install NVM (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Reload the shell so NVM becomes available
source ~/.bashrc

# Install and use Node.js 22
nvm install 22
nvm use 22

# Make Node.js 22 the default version
nvm alias default 22

# Verify the installed versions
node -v
npm -v

# Navigate to the frontend directory
cd ~/NestScanner/frontend

# Install project dependencies
npm install

# Start the Vite development server
npm run dev