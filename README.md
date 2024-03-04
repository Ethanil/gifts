# Clone git repo
navigate to your root directory and clone this repository with

```bash
git clone https://github.com/Ethanil/gifts
```
# Backend
## Install Python packages
navigate to the backend-directory and create a virtual environment for python and activate it
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

rename the .envExample into .env:
```bash
mv .envExample .env
```
and edit it with your credentials
### Generate secure secret key
To use JWT we need a proper secret key. Make sure to use a apropriate key-length for the chosen Hashing-Algorithm.
#### Generate Token for SH256 via Python interpreter
1. open the python interpreter by typing `py`
2. Import secrets module with `import secrets`
3. generate the token and print it with `print(secrets.token_urlsafe(32))` [you can change the length here]
4. copy and paste it to your .env-file

## Test the backend installation
To test that everything worked start the backend-server
```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```

if you want to test some more start another console and use
```bash
curl 127.0.0.1:5000/api/items
```

then stop the uvicorn-process with `ctrl+c`

deactivate the python-virtual-environment before proceding with
```bash
deactivate
```

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
command=%(ENV_HOME)s/gifts/gifts_backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 5000
autostart=true
autorestart=true
stdout_logfile=%(ENV_HOME)s/logs/gifts_backend.log
```
save and close with `ctrl+o` followed by `enter` and then `ctrl+x`

### Uberspace-config
expose the service to the outside(make sure to use the correct port and route):
```bash
uberspace web backend set /api --http --port 5000
```
# Frontend
## Setup
### Node
Navigate to the frontend and install the packages with
```bash
npm install
```
if this is not working for you try yarn instead:
```bash
yarn install
```

rename the .envExample:
```bash
mv .envExample .env
```
and edit your credentials

Build the frontend
```bash
npm run build
```
you can replace here `npm` with `yarn` aswell
you know should have an `.output/server/index.mjs` file. This is the entry-point of the node server.
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
stdout_logfile=%(ENV_HOME)s/logs/gifts_frontend.log
```
save and close with `ctrl+o` followed by `enter` and then `ctrl+x`

### Uberspace-config
expose the service to the outside(make sure to use the correct port and route):
```bash
uberspace web backend set / --http --port 8000
```
# Alternative supervisord setup
Alternatively you can create one group for both supervisord systems:
```
[group:gifts]
programs=gifts_frontend,gifts_backend

[program:gifts_backend]
directory=%(ENV_HOME)s/gifts/gifts_backend
command=%(ENV_HOME)s/gifts/gifts_backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 5000
autostart=true
autorestart=true
stdout_logfile=%(ENV_HOME)s/logs/gifts_backend.log

[program:gifts_frontend]
directory=%(ENV_HOME)s/gifts/gifts_frontend
command=node .output/server/index.mjs
autostart=true
autorestart=true
environment=NITRO_PORT=8000
stdout_logfile=%(ENV_HOME)s/logs/gifts_frontend.log
```
# Start supervisord
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

## check if everything works
check the backend port-routing with
```bash
uberspace web backend list
```
both ports should have an OK-status


# Port Database from php-giftreg to this app
## Users
```sql
INSERT into newSchema.user (avatar, email, firstName, lastName, password)
SELECT LOWER(u.email) as avatar, LOWER(u.email) as email, u.fullname as firstName, '' as lastName, u.password as password
FROM oldSchema.users u;
```
Add any kind of Lastname to users to not have ugly gaps in listnames
## Giftgroups/Lists
```sql
INSERT INTO newSchema.giftgroup (id, editable, isSecretGroup, name)
SELECT u.userid as id, false as editable, false as isSecretGroup, CONCAT(eu.firstName, ' ', eu.lastName, '''s Liste') as name
FROM oldSchema.users u join newSchema.user eu on u.fullname = eu.firstName;
```

## Beinggifted - Relation
```sql
INSERT INTO newSchema.isbeinggifted (giftGroup_id, user_email)
SELECT userid as id, LOWER(u.email) as user_email
FROM oldSchema.users u;
```

## Gifts
```sql
INSERT INTO newSchema.gift (name, price, giftStrength, link, description, picture, giftGroup_id, user_email, freeForReservation)
SELECT description AS name, price, ranking AS giftStrength, url AS link, test.items.comment AS description,  COALESCE(image_filename,'') AS picture, items.userid as giftGroup_id, LOWER(email) as user_email, false as freeForReservation
FROM oldSchema.items join oldSchema.users u on items.userid = u.userid;
```
make sure to copy the pictures of the gifts from the old directory into the one you chose in the `.env` of the backend!

## Reservations
```sql
INSERT INTO newSchema.has_reserved(gift_id, user_email)
SELECT g.id as gift_id, LOWER(u.email) as user_email
FROM oldSchema.allocs join items i on allocs.itemid = i.itemid join users u on allocs.userid = u.userid join newSchema.gift g on g.name = i.description
```

# Update Project
Navigate into your project directory(gifts)
## Get changes from github
Check if there are any updates with
```bash
git fetch
git status
```
if there are new/changed files this will show it

pull the changes with 
```
git pull
```
## Rebuild frontend
navigate into frontend-directory and run the install and build again
with npm:
```
npm install
npm run build
```
or with yarn:
```
yarn install
yarn run build
```
## Restart supervisor daemons
Restart the supervisore daemons with 
```
supervisorctl restart gifts_frontend
supervisorctl restart gifts_backend
```
or if those are the only 2 daemons running:
```
supervisorctl restart all
```

or if you used the alternative setup:
```
supervisorctl restart gifts:*
```