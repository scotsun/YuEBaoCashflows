from sshtunnel import SSHTunnelForwarder
from flask import Flask, render_template, request, flash
from flask_pymongo import PyMongo
from website import create_app,config

app = create_app()
if __name__ == '__main__':
    app.run(host=config['local']['localhost'],port=config['local']['port'],debug=True)
