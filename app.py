from sshtunnel import SSHTunnelForwarder
from flask import Flask, render_template, request, flash
from flask_pymongo import PyMongo
from website import create_app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
