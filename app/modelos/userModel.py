from flask_login import UserMixin

class User(UserMixin):
	
	def __init__(self,id,username,password,oficina,estado):
		self.id=id
		self.username=username
		self.password=password
		self.id_oficina=oficina
		self.estado=estado

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)