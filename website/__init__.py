from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from configparser import ConfigParser
from sshtunnel import SSHTunnelForwarder

config = ConfigParser()
config.read('config.ini')

tunnel = SSHTunnelForwarder(
	config['VM']['vm1_ip'],
	ssh_username=config['SSH']['ssh_username'],
	ssh_pkey=config['SSH']['ssh_pkey'],
	ssh_private_key_password=config['SSH']['ssh_private_key_password'],
	remote_bind_address=("127.0.0.1", 27017)
)
tunnel.start()
host = "localhost"
port = tunnel.local_bind_port
mongo = None

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'csse433'
	app.config['MONGO_URI'] = f'mongodb://{host}:{port}/yuebao'
	
	global mongo
	mongo = PyMongo(app)

	from .views import views
	from .auth import auth
	from .model import User

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.login_message = 'Please log in to access this page'
	login_manager.login_message_category = 'error'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(id):
		return User.get_by_id(id)

	app.register_blueprint(views, url_prefix = '/')
	app.register_blueprint(auth, url_prefix = '/')
	return app

