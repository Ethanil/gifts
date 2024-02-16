from flask import render_template
import config
from dotenv import load_dotenv
from os import getenv

app = config.connex_app
app.add_api(config.basedir / "openapi.yaml")
with app.app.app_context():
    config.db.create_all()

@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    load_dotenv()
    app.run(host=getenv('BACKEND_HOST'), port=int(getenv('BACKEND_PORT')))