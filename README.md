wsl


python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


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