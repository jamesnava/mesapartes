from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,SelectField
from wtforms.validators import DataRequired


class Documentos(FlaskForm):
	Asunto=StringField('Asunto',validators=[DataRequired()])
	TipoDoc=SelectField('Tipo Documento')
	Descripcion=StringField('Descripcion')
	Prioridad=SelectField('Prioridad')
	Estado=StringField('Estado')
	OffOrigen=StringField('Origen')
	OffDestino=StringField('Destino')
	CodigoSeguimiento=StringField('Cod Seguimiento')
	NroIE=StringField('Numero')
	Emisor=StringField('Emisor')
	guardar=SubmitField('Grabar')
