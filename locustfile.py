from locust import HttpUser, task, between
import random
import io

class UsuarioSimulado(HttpUser):
    wait_time = between(5, 15)   

    @task
    def insertar_documento(self):
        """Simula inserción de un documento."""
        # IDs que deben existir en la base de datos
        tipo_doc = random.choice([1, 2, 3,4,5,6,7,8,9,10])
        prioridad = random.choice([1, 2,3])
        oficinas_destino = random.sample(["AAMAA", "ADSXG", "AFFPT","AFRAA","APWVQ","ATSLD","AVHAO","BAGLI","BIVPW","BPZWX"], 2)  # usa IDs válidos

        # Documento de prueba (en memoria)
        archivo_fake = io.BytesIO(b"contenido de prueba")
        archivo_fake.name = "documento.txt"

        data = {
            "titulodoc": f"Documento generado por Locust {random.randint(1, 9999)}",
            "Asunto": "Prueba de rendimiento",
            "Tdoc": tipo_doc,
            "descripcion": "Documento de prueba simulado para test concurrente.",
            "prioridad": prioridad,
            "Emisor": "47584657",          # debe existir en PERSONA
            "idusuario": 1,                # debe existir en USUARIO
            "idoficinaorigen":"MYCUR",          # debe existir en OFICINA
            "oficinas[]": oficinas_destino,
            "codigos[]": oficinas_destino
        }

        files = {
            "adjunto": (archivo_fake.name, archivo_fake, "text/plain")
        }

        with self.client.post(
            "/documents/insertdocument",
            data=data,
            files=files,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                if '"movimiento":0' in response.text or '"movimiento":-1' in response.text:
                    response.failure(f"❌ Falló la inserción lógica: {response.text}")
                else:
                    response.success()
            else:
                response.failure(f"⚠️ Error HTTP {response.status_code}")

