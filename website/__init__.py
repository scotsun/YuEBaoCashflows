from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from configparser import ConfigParser
from sshtunnel import SSHTunnelForwarder
from kafka import KafkaProducer
import json

config = ConfigParser()
config.read('config.ini')
tunnels = [(config['VM']['mongos_bind'], int(config['VM']['mongos_port'])),(config['VM']['kafka_bind'],inr(config['VM']['kafka_port']))]
localPorts = [(config['local']['localhost'],int(config['local']['mongos_port'])),(config['local']['localhost'],inr(config['local']['kafka_port']))]
tunnel = SSHTunnelForwarder(
	config['VM']['vm2_ip'],
	ssh_username=config['SSH']['ssh_username'],
	ssh_pkey=config['SSH']['ssh_pkey'],
	ssh_private_key_password=config['SSH']['ssh_private_key_password'],
	remote_bind_addresses=tunnels,
	local_bind_addresses=localPorts
)
tunnel.start()
# host = "localhost"
# port = tunnel.local_bind_port
mongo = None
cassandra = None
producer = None

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'csse433'
	app.config['MONGO_URI'] = f'mongodb://{config['local']['localhost']}:{config['local']['mongos_port']}/yuebao'
	
	global mongo
	mongo = PyMongo(app)
	global cassandra
	cassandra = Cluster(['34.67.124.229']).connect('yuebao')
	cassandra.row_factory = dict_factory
	global producer
	producer = KafkaProducer(bootstrap_servers=f"{config['local']['localhost']}:{config['local']['kafka_port']}",value_serializer=lambda v: json.dumps(v).encode('utf-8'))

	from .views import views
	from .auth import auth
	from .model import User
	from .analytics import analytics

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
	app.register_blueprint(analytics, url_prefix='/')
	return app

