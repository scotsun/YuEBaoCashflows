from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from configparser import ConfigParser
from sshtunnel import SSHTunnelForwarder
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from flask_redis import FlaskRedis
import redis
from flask_caching import Cache

config = ConfigParser()
config.read('config.ini')
tunnel = SSHTunnelForwarder(
    config['VM']['vm3_ip'],
    ssh_username=config['SSH']['ssh_username'],
    ssh_pkey=config['SSH']['ssh_pkey'],
    ssh_private_key_password=config['SSH']['ssh_private_key_password'],
    remote_bind_addresses=[(config['local']['mongos_bind'],int(config['local']['mongos_port'])),("127.0.0.1",50000)]
    
)
# tunnel = SSHTunnelForwarder(
#     "35.223.217.140",
#     ssh_username="apple",
#     ssh_pkey="/Users/apple/Desktop/CSSE433/project-cli-keys/key-instance-1",
#     ssh_private_key_password="csse433",
#     remote_bind_address=("10.128.0.6", 40000)
# )
tunnel.start()
host = "localhost"
port1 = tunnel.local_bind_ports[0]
port2 = tunnel.local_bind_ports[1]
mongo = None
cassandra = None


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'csse433'
    app.config['MONGO_URI'] = f'mongodb://{host}:{port1}/yuebao'

    global mongo
    global cassandra
    global cache
    global redis_cli
    global redisConn
    mongo = PyMongo(app)

    cassandra = Cluster(['34.67.124.229']).connect('yuebao')
    cassandra.row_factory = dict_factory

    app.config['REDIS_URL'] = f'redis://{host}:{port2}'
    # redisConn = FlaskRedis(app)
    # redisConn = redis.Redis(host=host,port=port2)
    # test = redisConn.hgetall("book")
    # print(test)
    # redis_cli = redis.Redis(host=host,port=port )
    cache = Cache(app, config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_HOST':host, 'CACHE_REDIS_PORT':port2})
    # cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
    from .views import views
    from .auth import auth
    from .analytics import analytics

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(analytics, url_prefix='/')
    return app
