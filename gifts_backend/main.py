from flask import render_template
import config
# User, Gift, IsBeingGifted, GiftGroup, Comment,
from models import Event


app = config.connex_app
app.add_api(config.basedir / "openapi.yaml")
with app.app.app_context():
    config.db.create_all()

@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)