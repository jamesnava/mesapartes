from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
	usuario=StringField('Usuario',validators=[DataRequired()])
	clave=PasswordField('Contraseña',validators=[DataRequired()])
	recordar=BooleanField('Recordar')
	btnInicio=SubmitField('Iniciar')