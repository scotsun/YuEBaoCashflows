from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from configparser import ConfigParser
from sshtunnel import SSHTunnelForwarder
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

# config = ConfigParser()
# config.read('config.ini')
tunnel = SSHTunnelForwarder(
    "35.223.217.140",
    ssh_username="apple",
    ssh_pkey="/Users/apple/Desktop/CSSE433/project-cli-keys/key-instance-1",
    ssh_private_key_password="csse433",
    remote_bind_address=("10.128.0.6", 40000)
)
tunnel.start()
host = "localhost"
port = tunnel.local_bind_port
mongo = None
cassandra = None


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'csse433'
    app.config['MONGO_URI'] = f'mongodb://{host}:{port}/yuebao'

    global mongo
    global cassandra
    mongo = PyMongo(app)

    cassandra = Cluster(['34.67.124.229']).connect('yuebao')
    cassandra.row_factory = dict_factory

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    return app
