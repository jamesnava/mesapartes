import plotly.express as px
import plotly.io as pio
import pandas as pd

def grafico_documentos_por_oficina(data):
	df = pd.DataFrame(data)
	#df["OficinaCorta"]=df["Oficina"].str.slice(12,25)
	df["Oficina_"]=df["Oficina"].apply(lambda x: " ".join(x.split()[2:4]))
	fig = px.bar(df, y="Cantidad", x="Oficina_",color="Oficina",height=300,text="Cantidad")
	fig.update_layout(xaxis_tickangle=-30,showlegend=False,xaxis_tickfont=dict(size=10))
	fig.update_xaxes(tickson="boundaries")
	return pio.to_html(fig, full_html=False,config={'displayModeBar': False})

