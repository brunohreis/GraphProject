import os
import sys
import logging

caminho_absoluto = os.path.abspath(os.curdir)
sys.path.insert(0,caminho_absoluto)

from project.backend.createMap import converter_kml_para_csv, createMap
from project.backend.api import obter_coordenadas
from project.backend.routeGenerator import generate_route


end_inicial = sys.argv[1]
end_final = sys.argv[2]

# Gera as Rotas (PROPENSO A ERROS)
generate_route(end_inicial, end_final)

# Tentativa de converter KML para CSV.
kml_input_filename = "minimum_path_custom.kml"
csv_output_filename_from_kml = "rota1.csv"

# ! Nota: converter_kml_para_csv espera que o arquivo KML de entrada esteja em 'project/rotas/'
# ! e o arquivo CSV de saída também será salvo em 'project/rotas/' devido à sua lógica interna.

if not converter_kml_para_csv(kml_input_filename, csv_output_filename_from_kml):
    print(f"ERRO_CONVERSAO_KML: Falha ao converter '{kml_input_filename}' para '{csv_output_filename_from_kml}'.")
    sys.exit(1)

try:
    output_map1_path = "project/mapas/mapa_min_dist.html"
    output_map2_path = "project/mapas/mapa_min_time.html"

    # Processa o primeiro mapa
    if not createMap("rota1.csv", "mapa_min_dist.html"):
        # createMap retornou False, indicando falha (e já imprimiu detalhes).
        # Middleware adiciona seu prefixo padronizado e sai.
        print("ERRO_CRIACAO_MAPA: Falha ao criar mapa para 'rota1.csv'. Detalhes devem estar nos logs do console de createMap.")
        sys.exit(1)
    # Verificação adicional: se createMap retornou True, mas o arquivo não existe.
    elif not os.path.exists(output_map1_path):
        print(f"ERRO_CRIACAO_MAPA: createMap para 'rota1.csv' indicou sucesso, mas o arquivo '{output_map1_path}' não foi encontrado.")
        sys.exit(1)

    # # Processa o segundo mapa
    # if not createMap("rota.csv", "mapa_min_time.html"):
    #     print("ERRO_CRIACAO_MAPA: Falha ao criar mapa para 'rota.csv'. Detalhes devem estar nos logs do console de createMap.")
    #     sys.exit(1)
    # elif not os.path.exists(output_map2_path):
    #     print(f"ERRO_CRIACAO_MAPA: createMap para 'rota.csv' indicou sucesso, mas o arquivo '{output_map2_path}' não foi encontrado.")
    #     sys.exit(1)

    # Se tudo correu bem para ambos os mapas
    print(f"{output_map1_path}|{output_map2_path}")

except FileNotFoundError as e:
    print(f"ERRO_CRIACAO_MAPA: Operação de arquivo falhou - {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERRO_CRIACAO_MAPA: Erro inesperado no processo de middleware - {type(e).__name__}: {e}")
    sys.exit(1)
