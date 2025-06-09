import googlemaps
import os
from datetime import datetime  # noqa: F401 # type: ignore
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def obter_coordenadas(endereco):
    # Obter a chave da API das variáveis de ambiente
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    if not API_KEY: # Verifica se a chave foi carregada
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!! ATENÇÃO: Chave da API do Google Maps não configurada !!!
        # !!! Verifique seu arquivo .env e a variável            !!!
        # !!! GOOGLE_MAPS_API_KEY.                               !!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return False
    

    gmaps_client =  googlemaps.Client(key=API_KEY)
    try:
        geocode_result = gmaps_client.geocode(endereco, region='br')

        if geocode_result:
            # A estrutura interna do resultado é a mesma do JSON original
            location = geocode_result[0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
                
            return [latitude, longitude]
        else:
            # Nenhum resultado encontrado para o endereço.
            return False
                
    except Exception:
        return False
