import os
import subprocess
import sys
import csv

# ATENÇÃO: Desabilitar o sandbox reduz a segurança.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

from PyQt5.QtCore import QFileInfo, pyqtSignal, QThread, Qt, QUrl
from PyQt5.QtGui import QMovie
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QMessageBox, QPushButton,
                             QStackedWidget, QVBoxLayout, QWidget, QComboBox)


# Tela inicial: Coleta os endereços de partida e destino do usuário.
class TelaInicial(QWidget):
    def __init__(self, prosseguir_callback):
        super().__init__()
        self.prosseguir_callback = prosseguir_callback
        layout = QVBoxLayout(self)
        group_box = QGroupBox("Preencha os dados")
        form_layout = QFormLayout()

        # Dicionário: nome exibido → id para envio ao backend
        self.nome_para_id = {}

        # Leitura do CSV sem cabeçalho
        with open("project/rotas/Relevant_index.csv", encoding="utf-8") as f:
            leitor = csv.reader(f, delimiter=";")
            for linha in leitor:
                if len(linha) >= 2:
                    id_ = linha[0].strip()
                    if linha[1].strip() != "None":
                        nome = linha[1].strip()
                        if linha[2].strip() != "None":
                            nome +=  " - " + linha[2].strip()
                        if linha[3].strip() != "None":
                            nome +=  " - " + linha[3].strip()
                    else:
                        if linha[3].strip() != "None":
                            nome = linha[3].strip()
                            if linha[2].strip() != "None":
                                nome +=  " - " + linha[2].strip()
                    self.nome_para_id[nome] = id_

        # Criação dos combo boxes com preenchimento dinâmico
        self.end_inicial_input = QComboBox()
        self.end_inicial_input.setEditable(False)
        self.end_inicial_input.addItem("Selecione um endereço...")
        self.end_inicial_input.addItems(self.nome_para_id.keys())
        self.end_inicial_input.setInsertPolicy(QComboBox.NoInsert)

        self.end_final_input = QComboBox()
        self.end_final_input.setEditable(False)
        self.end_final_input.addItem("Selecione um endereço...")
        self.end_final_input.addItems(self.nome_para_id.keys())
        self.end_final_input.setInsertPolicy(QComboBox.NoInsert)

        self.botao_prosseguir = QPushButton("Prosseguir e Executar Backend")

        form_layout.addRow(QLabel("Ponto de partida:"), self.end_inicial_input)
        form_layout.addRow(QLabel("Ponto de destino:"), self.end_final_input)
        form_layout.addRow(self.botao_prosseguir)

        group_box.setLayout(form_layout)
        layout.addWidget(group_box)

        self.botao_prosseguir.clicked.connect(self.prosseguir)

    def prosseguir(self):
        nome_inicial = self.end_inicial_input.currentText()
        nome_final = self.end_final_input.currentText()

        if nome_inicial == "Selecione um endereço..." or nome_inicial not in self.nome_para_id:
            QMessageBox.warning(self, "Atenção", "Selecione um ponto de partida válido.")
            return
        if nome_final == "Selecione um endereço..." or nome_final not in self.nome_para_id:
            QMessageBox.warning(self, "Atenção", "Selecione um ponto de destino válido.")
            return

        id_inicial = self.nome_para_id[nome_inicial]
        id_final = self.nome_para_id[nome_final]

        self.prosseguir_callback(id_inicial, id_final)


# Tela de carregamento: Exibe uma animação enquanto o backend processa os dados.
class TelaDeCarregamento(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.loading_label = QLabel()
        self.movie = QMovie("project/assets/loading.gif")
        self.loading_label.setMovie(self.movie)

        layout.addWidget(QLabel("Processando no backend, por favor aguarde..."))
        layout.addWidget(self.loading_label)

    def start_animation(self):
        self.movie.start()

    def stop_animation(self):
        self.movie.stop()

# Tela de resultados: Exibe os mapas gerados e permite a navegação entre eles.
class TelaDeResultado(QWidget):
    def __init__(self, voltar_callback):
        super().__init__()
        self.voltar_callback = voltar_callback
        self.caminho_arquivo_resultado = []

        layout = QVBoxLayout(self)
        botoes_layout = QHBoxLayout()

        self.botao_mapa_1 = QPushButton("Mapa Menor Distância")
        self.botao_mapa_2 = QPushButton("Mapa Menor Tempo")
        self.botao_mapa_3 = QPushButton("Opção 3 (2)")
        self.botao_voltar = QPushButton("Voltar ao Início")

        botoes_layout.addWidget(self.botao_mapa_1)
        botoes_layout.addWidget(self.botao_mapa_2)
        botoes_layout.addWidget(self.botao_mapa_3)
        botoes_layout.addWidget(self.botao_voltar)

        self.browser = QWebEngineView()
        self.browser.setHtml("<h2 style='text-align:center;'>Backend finalizado. Escolha uma opção de mapa acima.</h2>")

        layout.addLayout(botoes_layout)
        layout.addWidget(self.browser)

        self.botao_mapa_1.clicked.connect(lambda: self.on_botao_mapa_clicked(0))
        self.botao_mapa_2.clicked.connect(lambda: self.on_botao_mapa_clicked(1))
        self.botao_mapa_3.clicked.connect(lambda: self.on_botao_mapa_clicked(2))
        self.botao_voltar.clicked.connect(self.voltar_callback)

    def receber_caminho_resultado(self, caminho_arquivo_string):
        print(f"Recebido do backend (string): {caminho_arquivo_string}")
        self.caminho_arquivo_resultado = caminho_arquivo_string.strip().split("|")
        print(f"Caminhos armazenados (lista): {self.caminho_arquivo_resultado}")

    def on_botao_mapa_clicked(self, indice_mapa):
        print(f"Botão clicado, solicitando mapa com índice: {indice_mapa}")
        if not self.caminho_arquivo_resultado or indice_mapa >= len(self.caminho_arquivo_resultado):
            self.browser.setHtml(f"<h1>Erro: O resultado para o mapa {indice_mapa + 1} não está disponível.</h1>")
            print(f"Erro: tentativa de acessar índice {indice_mapa} em uma lista de tamanho {len(self.caminho_arquivo_resultado)}.")
            return

        caminho_selecionado = self.caminho_arquivo_resultado[indice_mapa]
        self.carregar_html(caminho_selecionado)

    def carregar_html(self, caminho_arquivo):
        if caminho_arquivo:
            caminho_absoluto = QFileInfo(caminho_arquivo).absoluteFilePath()
            self.browser.setUrl(QUrl.fromLocalFile(caminho_absoluto))
        else:
            self.browser.setHtml("<h1>Erro: O caminho do arquivo está vazio.</h1>")

# Worker para executar o script de backend em uma thread separada, evitando que a UI congele.
class BackendWorker(QThread):
    terminado = pyqtSignal(str)
    def __init__(self, end_inicial, end_final):
        super().__init__()
        self.end_inicial = end_inicial
        self.end_final = end_final

    def run(self):
        try:
            # Prepara o ambiente para o subprocesso garantir saída UTF-8 (assim não faltará caracteres)
            sub_env = os.environ.copy()
            sub_env["PYTHONIOENCODING"] = "utf-8"

            # Executa o middleware, captura a saída como string.
            resultado_str = subprocess.check_output(
                [sys.executable, "-m", "project.middleware.middleware", self.end_inicial, self.end_final],
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='strict',    # Se não for UTF-8, é um erro
                env=sub_env
            )
            self.terminado.emit(resultado_str.strip())
        except subprocess.CalledProcessError as e:
            # Se o middleware falhar, e.output será sua saída (já uma string devido ao parâmetro 'encoding')
            # Se e.output for None (ex: comando não encontrado), fornece uma mensagem genérica de e
            error_output_str = e.output.strip() if e.output else f"Erro no subprocesso: {str(e)}"
            
            # Emitir diretamente a saída do subprocesso.
            # backend_finalizado fará a análise dos prefixos "ERRO_API:", "ERRO_CRIACAO_MAPA:",
            # ou tratará como saída inesperada (que cairá no "Erro de Resultado").
            self.terminado.emit(error_output_str)
        except Exception as e:
            self.terminado.emit(f"ERRO_INESPERADO_WORKER: {str(e)}")

# Janela principal: Gerencia a navegação entre as diferentes telas da aplicação.
class JanelaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho de Grafos - Tema 1")
        self.setGeometry(100, 100, 800, 700)

        self.stacked_widget = QStackedWidget()
        self.tela_inicial = TelaInicial(self.iniciar_processamento_backend)
        self.tela_carregamento = TelaDeCarregamento()
        self.tela_resultado = TelaDeResultado(self.voltar_para_tela_inicial)

        self.stacked_widget.addWidget(self.tela_inicial)
        self.stacked_widget.addWidget(self.tela_carregamento)
        self.stacked_widget.addWidget(self.tela_resultado)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)

    def iniciar_processamento_backend(self, end_inicial, end_final):
        self.stacked_widget.setCurrentWidget(self.tela_carregamento)
        self.tela_carregamento.start_animation()

        self.worker = BackendWorker(end_inicial, end_final)
        self.worker.terminado.connect(self.backend_finalizado)
        self.worker.start()

    def backend_finalizado(self, resultado_backend):
        """
        Este método é chamado quando o BackendWorker finaliza.
        Ele processa o resultado do backend, que pode ser uma string de sucesso
        (caminhos dos mapas separados por "|") ou uma string de erro.

        Origem das strings de erro processadas aqui:
        - "ERRO_API:...": Diretamente da saída do middleware.py, se falha na API de geocodificação.
        - "ERRO_CRIACAO_MAPA:...": Diretamente da saída do middleware.py, se falha na criação dos mapas HTML.
        - "ERRO_CONVERSAO_KML:...": Diretamente da saída do middleware.py, se falha na conversão de KML para CSV.
        - "ERRO_INESPERADO_WORKER:...": Emitido pelo BackendWorker se ocorrer uma exceção DENTRO
                                      do próprio método run() do BackendWorker (que não seja
                                      CalledProcessError, como um erro de programação no worker).
        - Qualquer outra string (ex: traceback do Python de middleware.py):
                          Será tratado pelo caso "Erro de Resultado".
        
        Se 'resultado_backend' não contiver um dos prefixos de erro conhecidos acima
        e não for uma string de sucesso válida (ou seja, não contiver "|"), 
        é tratado como um "Erro de Resultado".

        Em todos os casos de erro, um QMessageBox é exibido e o usuário é retornado à tela inicial.
        """
        self.tela_carregamento.stop_animation()

        error_title = None
        error_message_template = None
        error_detail_for_log = None
        log_console_prefix = None

        if resultado_backend.startswith("ERRO_API:"):
            error_title = "Erro de Geocodificação"
            log_console_prefix = "API Geocoding"
            error_detail_for_log = resultado_backend.replace("ERRO_API: ", "", 1)
            error_message_template = "Ocorreu um erro ao buscar as coordenadas:\n{error_detail}\nPor favor, verifique os endereços e tente novamente."
        elif resultado_backend.startswith("ERRO_CRIACAO_MAPA:"):
            error_title = "Erro na Criação do Mapa"
            log_console_prefix = "Map Creation"
            error_detail_for_log = resultado_backend.replace("ERRO_CRIACAO_MAPA: ", "", 1)
            error_message_template = "Ocorreu um erro durante a criação dos mapas:\n{error_detail}\nVerifique os arquivos de rotas e tente novamente."
        elif resultado_backend.startswith("ERRO_CONVERSAO_KML:"):
            error_title = "Erro na Conversão KML"
            log_console_prefix = "KML Conversion"
            error_detail_for_log = resultado_backend.replace("ERRO_CONVERSAO_KML: ", "", 1)
            error_message_template = "Ocorreu um erro durante a conversão do arquivo KML para CSV:\n{error_detail}\nVerifique o arquivo KML e tente novamente."
        elif resultado_backend.startswith("ERRO_INESPERADO_WORKER:"):
            error_title = "Erro Interno"
            log_console_prefix = "Unexpected Worker"
            error_detail_for_log = resultado_backend.replace("ERRO_INESPERADO_WORKER: ", "")
            error_message_template = "Ocorreu um erro inesperado no processamento.\nDetalhes: {error_detail}\nPor favor, tente novamente."
        # Para resultados que não correspondem a prefixos de erro conhecidos mas não são caminhos de mapa válidos
        elif not resultado_backend or "|" not in resultado_backend: 
            error_title = "Erro de Resultado"
            log_console_prefix = "Invalid backend result"
            error_detail_for_log = resultado_backend
            error_message_template = "O backend retornou um resultado inesperado ou vazio: '{error_detail}'.\nNão foi possível carregar os mapas."
        else:
            # Caso de sucesso
            self.tela_resultado.receber_caminho_resultado(resultado_backend)
            self.stacked_widget.setCurrentWidget(self.tela_resultado)
            return

        # Cria a tela de erro com base no formulário escrito pelos Erros anteriormente
        # Também substitui o {error_detail} pelo error_detail_for_log
        if error_title:
            QMessageBox.critical(self, error_title, error_message_template.format(error_detail=error_detail_for_log))
            print(f"{log_console_prefix} Error: {error_detail_for_log}") # Log de console para depuração
            self.stacked_widget.setCurrentWidget(self.tela_inicial)

    def voltar_para_tela_inicial(self):
        self.tela_resultado.browser.setHtml("<h2 style='text-align:center;'>Backend finalizado. Clique no botão acima para ver o resultado.</h2>")
        self.stacked_widget.setCurrentWidget(self.tela_inicial)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec_())
