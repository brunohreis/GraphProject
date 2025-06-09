import csv
import xml.etree.ElementTree as ET

import folium
import pandas as pd

def createMap(ARQUIVO_CSV: str, nome_arquivo_saida: str):
    
    # --- 1. Carregar os dados da rota ---
    try:
        df = pd.read_csv(f"project/rotas/{ARQUIVO_CSV}")
    except FileNotFoundError:
        return False

    # Verificar se o arquivo tem dados
    if df.empty:
        return False
    
    # --- 2. Preparar os dados para o Folium ---
    # Converte as colunas de latitude e longitude em uma lista de pares de coordenadas
    # Ex: [[lat1, lon1], [lat2, lon2]]
    rota_coordenadas = df[['latitude', 'longitude']].values.tolist()

    # Identifica o ponto inicial e final da rota
    ponto_inicial = rota_coordenadas[0]
    ponto_final = rota_coordenadas[-1]

    # --- 3. Criar o mapa base ---
    # Centraliza o mapa no ponto médio da rota para melhor visualização
    mapa = folium.Map(
        location=df[['latitude', 'longitude']].mean().values.tolist(),
        zoom_start=14  # Um zoom mais próximo, ideal para rotas
    )

    # --- 4. Adicionar a linha da rota ao mapa ---
    # folium.PolyLine desenha uma linha conectando os pontos na ordem fornecida
    folium.PolyLine(
        locations=rota_coordenadas,
        color='blue',
        weight=5,
        opacity=0.8
    ).add_to(mapa)

    # --- 5. Adicionar marcadores de Início e Fim ---
    # Marcador para o Ponto Inicial (verde)
    folium.Marker(
        location=ponto_inicial,
        popup='<strong>Ponto Inicial</strong>',
        tooltip='Início da Rota',
        icon=folium.Icon(color='green', icon='play')
    ).add_to(mapa)

    # Marcador para o Ponto Final (vermelho)
    folium.Marker(
        location=ponto_final,
        popup='<strong>Ponto Final</strong>',
        tooltip='Fim da Rota',
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(mapa)

    # --- 6. Salvar o resultado ---
    try:
        mapa.save(f'project/mapas/{nome_arquivo_saida}')
        return True # Sinaliza sucesso
    except Exception:
        return False # Sinaliza falha

# Lê um arquivo KML, extrai todas as coordenadas de todas as tags <coordinates>
# e as salva em um arquivo CSV com as colunas 'latitude' e 'longitude'.
def converter_kml_para_csv(arquivo_kml_entrada: str, arquivo_csv_saida: str):
    try:
        # --- 1. Análise do Arquivo KML ---
        # Usamos um parser de XML para ler o arquivo KML de forma estruturada.
        tree = ET.parse(f"project/rotas/{arquivo_kml_entrada}")
        root = tree.getroot()
        
        # A sintaxe './/{*}coordinates' encontra a tag <coordinates> em qualquer lugar
        # do arquivo, ignorando os "namespaces" do XML.
        coordenadas_tags = root.findall('.//{*}coordinates')

        if not coordenadas_tags:
            return False

        # Lista para armazenar todos os pares [latitude, longitude]
        pontos_processados = []

        # --- 2. Extração e Processamento das Coordenadas ---
        for tag in coordenadas_tags:
            # Pega o texto de dentro da tag, que é uma longa string de coordenadas
            # .strip() remove espaços e quebras de linha extras do início e do fim.
            texto_coordenadas = tag.text.strip()
            lista_de_pontos = texto_coordenadas.split()
            
            for ponto_str in lista_de_pontos:
                # .split(',') quebra em ['-46.68233', '-23.58693', '0']
                coords = ponto_str.split(',')
                
                if len(coords) >= 2:
                    longitude = coords[0]
                    latitude = coords[1]
                    
                    pontos_processados.append([latitude, longitude])

        # --- 3. Escrita do Arquivo CSV ---
        if not pontos_processados:
            return False

        with open(f"project/rotas/{arquivo_csv_saida}", mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escreve o cabeçalho (header) do CSV
            writer.writerow(['latitude', 'longitude'])
            
            # Escreve todas as linhas de dados de uma vez
            writer.writerows(pontos_processados)

        return True # Sinaliza sucesso

    except Exception:
        return False
