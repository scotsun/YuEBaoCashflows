from . import mongo
import uuid
from flask_login import UserMixin

class User(UserMixin):
	def __init__(self, username, email, password, _id=None):
		self.username = username
		self.email = email
		self.password = password
		self._id = uuid.uuid4().hex if _id is None else _id

	def get_id(self):
		return self._id

	@classmethod
	def get_by_email(cls, email):
		data = mongo.db.appUser.find_one({"email": email})
		if data is not None:
			return cls(**data)

	@classmethod
	def get_by_username(cls, username):
		data = mongo.db.appUser.find_one({"username": username})
		if data is not None:
			return cls(**data)

	@classmethod
	def get_by_id(cls, _id):
		data = mongo.db.appUser.find_one({"_id": _id})
		if data is not None:
			return cls(**data)
	
	@classmethod
	def register(cls, username, email, password):
		user = cls.get_by_email(email)
		if user is None:
			new_user = cls(username, email, password)
			new_user.save_to_mongo()
			# session['email'] = email
			return True
		else:
			return False

	def jsonify(self):
		return {
			"username":self.username,
			"email": self.email,
			"_id": self._id,
			"password": self.password,
			"reports":[]
		}


	def save_to_mongo(self):
		mongo.db.appUser.insert(self.jsonify())

