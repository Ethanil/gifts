# Clone git repo
navigate to your root folder and clone this repository with

```bash
git clone https://github.com/Ethanil/gifts
```

# Install Python packages
navigate to the backend-folder and create a virtual environment for python and activate it
```bash
cd gifts/gifts_backend
```
```bash
python3.10 -m venv .venv
```
```bash
source .venv/bin/activate
```

you will now see a `(.venv)` in front of your username in the console

install the packages with

```bash
python3.10 -m pip install -r requirements.txt
```

# Nuxt 3 Minimal Starter

Look at the [Nuxt 3 documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install the dependencies:

```bash
# npm
npm install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build
```

Locally preview production build:

```bash
# npm
npm run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

```
[program:gifts_frontend]
directory=/home/ethanil/giftSharing
command=node .output/server/index.mjs --prefix %(ENV_HOME)s/giftSharing/
autostart=true
autorestart=true
```