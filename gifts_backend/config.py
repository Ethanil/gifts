import os
import pathlib
import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv

load_dotenv()
basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.FlaskApp(__name__, specification_dir=basedir)
connex_app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app = connex_app.app


app.config["SQLALCHEMY_DATABASE_URI"] = f"mariadb+mariadbconnector://{os.getenv('DATABASE_USERNAME')}:{os.getenv('DATABASE_PASSWORD')}@localhost/{os.getenv('DATABASE_SCHEMA_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)

ma = Marshmallow(app)
