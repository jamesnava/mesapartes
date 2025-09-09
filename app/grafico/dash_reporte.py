import plotly.express as px
import plotly.io as pio
import pandas as pd

def grafico_documentos_por_oficina():
	df = pd.DataFrame({
        "Oficina": ["Estadística", "Administración", "Tesorería", "RRHH"],
        "Documentos": [120, 95, 70, 110]
    })
	fig = px.bar(df, x="Oficina", y="Documentos", title="Documentos por oficina")
	return pio.to_html(fig, full_html=False)

