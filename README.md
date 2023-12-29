# Clone git repo
navigate to your root folder and clone this repository with

```bash
git clone https://github.com/Ethanil/gifts
```
# Backend
## Install Python packages
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
pip install -r requirements.txt
```


## Test the backend installation
To test that everything worked start the backend-server
```bash
uvicorn main:app --host 127.0.0.1 --port 5000
```

if you want to test some more start another console and use
```bash
curl 127.0.0.1:5000/api/items
```

then stop the uvicorn-process with `ctrl+c`

## Setup supervisord daemon
### Create daemon.ini
Navigate into your service.d directory with
```bash
cd ~/etc/services.d/
```

And create a gifts_backend.ini with
```bash
nano gifts_backend.ini
```
paste the following code into it
```
[program:gifts_backend]
directory=%(ENV_HOME)s/gifts/gifts_backend
command=%(ENV_HOME)s/gifts/gifts_backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 5000
autostart=true
autorestart=true
stdout_logfile=%(ENV_HOME)s/logs/gifts_backend.log
```
save and close with `ctrl+o` followed by `enter` and then `ctrl+x`
### Start supervisord
reread the config
```bash
supervisorctl reread
```
update the services
```bash
supervisorctl update
```
after a few seconds you should see the process running with
```bash
supervisorctl status
```

# Frontend
## Setup
### Node
Navigate to the frontend and install the packages with
```bash
npm install
```
### supervisord
Navigate into your service.d directory with
```bash
cd ~/etc/services.d/
```
And create a gifts_frontend.ini with
```bash
nano gifts_frontend.ini
```
paste the following code into it
```
[program:gifts_frontend]
directory=%(ENV_HOME)s/gifts/gifts_frontend
command=node .output/server/index.mjs
autostart=true
autorestart=true
environment=NITRO_PORT=8000
stdout_logfile=%(ENV_HOME)s/logs/gifts_backend.log
```
save and close with `ctrl+o` followed by `enter` and then `ctrl+x`

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