# FrontendGrafos

This is a Python application for graph visualization.

## Configuração do Projeto

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

- Python 3.12.x instalado
- pip

### Passos para Configuração

1. **Clone o repositório:**

    ```bash
    git clone https://github.com/brunohreis/GraphProject.git
    cd GraphProject
    ```

2. **Instale o Poetry:**
    Poetry é um gerenciador de dependências e empacotamento para Python. Se você ainda não o tem instalado, pode instalá-lo via pip:

    ```bash
    pip install poetry
    ```

    Para mais detalhes sobre a instalação do Poetry, consulte a [documentação oficial do Poetry](https://python-poetry.org/docs/#installation).

3. **Instale as dependências do projeto:**
    Com o Poetry instalado, navegue até a raiz do projeto (onde o arquivo `pyproject.toml` está localizado) e execute o seguinte comando para instalar todas as dependências definidas no projeto:

    ```bash
    poetry install
    ```

    Este comando criará um ambiente virtual (se não existir) e instalará todas as bibliotecas necessárias.

4. **Execute o projeto:**
    Para ativar o ambiente virtual gerenciado pelo Poetry e executar a aplicação principal, utilize:

    ```bash
    poetry run python project/main.py
    ```
