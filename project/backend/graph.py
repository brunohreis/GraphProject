import matplotlib.pyplot as plt
import networkx as nx

class Vertex:
    def __init__(self, lat, lon):
        self.lat = float(lat)
        self.lon = float(lon)

    def __hash__(self):
        return hash((self.lat, self.lon))

    def __eq__(self, other):
        return (
            isinstance(other, Vertex)
            and self.lat == other.lat
            and self.lon == other.lon
        )

    def __repr__(self):
        return f"Vertex({self.lat}, {self.lon})"
    
    # Método auxiliar para serialização no formato 'lat,lon'
    def to_file_string(self):
        return f"{self.lat},{self.lon}"

class GraphEdge:
    def __init__(self, ending_vertex, weight):
        self.ending_vertex = ending_vertex
        self.weight = weight

    def __repr__(self):
        return f"GraphEdge(to: {self.ending_vertex}, weight: {self.weight})"
    
    def to_file_string(self):
        return f"{self.ending_vertex.lat},{self.ending_vertex.lon},{self.weight}"



class Edge:
    def __init__(self, beginning_vertex, graph_edge):
        self.beginning = beginning_vertex
        self.edge = graph_edge

    def __repr__(self):
        return f"Edge(from: {self.beginning}, to: {self.edge.ending_vertex}, weight: {self.edge.weight})"


class Graph:
    def __init__(self):
        # Adjacency list usando um dicionário
        self.adj_lists = {}

    def add_vertex(self, vertex):
        if vertex not in self.adj_lists:
            self.adj_lists[vertex] = []

    def add_edge(self, beginning_vertex, graph_edge):
        self.add_vertex(beginning_vertex)
        self.add_vertex(graph_edge.ending_vertex)
        self.adj_lists[beginning_vertex].append(graph_edge)

    def get_edge(self, v_start, v_end):
        if v_start in self.adj_lists:
            for edge in self.adj_lists[v_start]:
                if edge.ending_vertex == v_end:
                    return Edge(v_start, edge)
        return None

    def _dijkstra(self, origin, destination):
        # Inicialização (equivalente a 'Initialization' em Java)
        dist = {v: float("inf") for v in self.adj_lists.keys()}
        pred = {v: None for v in self.adj_lists.keys()}

        # Lista de vértices explorados, começa apenas com a origem
        explored = []

        # A distância da origem para ela mesma é 0
        dist[origin] = 0.0
        # O primeiro vértice explorado é a origem
        explored.append(origin)

        counter = 0
        # O loop principal continua enquanto o destino não for alcançado.
        while dist.get(destination) == float("inf") and counter < len(self.adj_lists):
            min_weight = float("inf")
            to_be_added = None
            predecessor = None

            # Itera sobre todos os vértices já explorados (equivalente a 'for(int i=0; i<exp.size(); i++)')
            for v_explored in explored:
                if v_explored in self.adj_lists:
                    # Itera sobre os vizinhos do vértice explorado
                    for edge in self.adj_lists[v_explored]:
                        w_neighbor = edge.ending_vertex

                        # A condição principal: o vizinho não foi explorado e o caminho até ele é o menor encontrado até agora
                        if (
                            w_neighbor not in explored
                            and (dist[v_explored] + edge.weight) < min_weight
                        ):
                            # Se o vértice w não foi explorado, a aresta pertence ao corte
                            min_weight = dist[v_explored] + edge.weight
                            to_be_added = w_neighbor
                            predecessor = v_explored

            # Se um novo vértice para adicionar foi encontrado
            if to_be_added is not None:
                dist[to_be_added] = min_weight
                pred[to_be_added] = predecessor
                explored.append(to_be_added)
                counter += 1
            else:
                # Se nenhum vértice novo puder ser adicionado, o grafo é desconectado
                # ou todos os nós alcançáveis foram visitados.
                break

        return dist, pred

    def get_shortest_path(self, origin, destination):
        """
        Encontra o caminho mais curto entre a origem e o destino usando o método de Dijkstra
        e reconstrói o caminho.
        """
        dist, pred = self._dijkstra(origin, destination)

        # Se a distância até o destino for infinita, não há caminho
        if dist.get(destination, float("inf")) == float("inf"):
            return None

        path = []
        current = destination

        # Volta do destino até a origem usando os predecessores
        while current is not None and current != origin:
            prev = pred.get(current)
            if prev is None:
                break

            edge = self.get_edge(prev, current)
            if edge is not None:
                path.insert(0, edge)

            current = prev

        return path

    def num_nodes(self):
        return len(self.adj_lists)

    def num_edges(self):
        return sum(len(edges) for edges in self.adj_lists.values())

    def save_image(self, filename):
        """
        Gera uma visualização do grafo parametrizado, convertendo-o para um grafo do tipo networkx
        """
        # 1. Cria um grafo vazio na biblioteca networkx
        g_nx = nx.Graph()

        # 2. Itera sobre a lista de adjacências do grafo customizado para adicionar nós e arestas
        if not self.adj_lists:
            # print("O grafo está vazio. Não há nada para visualizar.")
            return

        # Dicionário para armazenar as posições (lat, lon) de cada nó
        pos = {}

        for vertex, edges in self.adj_lists.items():
            # Adiciona o nó ao grafo networkx e guarda sua posição
            g_nx.add_node(vertex)
            pos[vertex] = (vertex.lon, vertex.lat)

            # Adiciona as arestas correspondentes
            for graph_edge in edges:
                g_nx.add_edge(
                    vertex, graph_edge.ending_vertex, weight=graph_edge.weight
                )

        # 3. Desenha o grafo usando as posições geográficas
        plt.figure(figsize=(12, 8))
        nx.draw(
            g_nx,
            pos,
            node_size=10,
            node_color="blue",
            edge_color="gray",
            with_labels=False,
        )

        plt.title("Visualização do grafo (lon x lat)")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.savefig(filename)
        plt.close()

    def write_graph_to_file(self, filename):
        """
        Salva o estado atual do objeto Graph em um arquivo de texto
        Formato de cada linha: "lat_vertex,lon_vertex;lat_edge_end1,lon_edge_end1,weight1;..."
        """
        try:
            with open(filename, 'w') as f:
                for vertex, edges in self.adj_lists.items():
                    line_parts = [vertex.to_file_string()]
                    for edge in edges:
                        line_parts.append(edge.to_file_string())
                    f.write(";".join(line_parts) + "\n")
            # print(f"Grafo salvo com sucesso em '{filename}'")
        except Exception as e:
            # print(f"Erro ao salvar o grafo em '{filename}': {e}")
            pass

    @staticmethod
    def get_graph_from_file(filename):
        """
        Carrega um objeto Graph de um arquivo de texto,
        retornando uma nova instância da classe Graph.
        """
        rv = Graph() # Nova instância do grafo
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip() # Remove espaços em branco e nova linha
                    if not line: # Ignora linhas vazias
                        continue

                    parts = line.split(";")
                    if not parts:
                        continue

                    # O primeiro elemento é o vértice de origem (chave)
                    key_vertex_str = parts[0]
                    key_vertex_coords = key_vertex_str.split(",")
                    if len(key_vertex_coords) != 2:
                        continue
                    try:
                        lat = float(key_vertex_coords[0])
                        lon = float(key_vertex_coords[1])
                        key_vertex = Vertex(lat, lon)
                        rv.add_vertex(key_vertex) # Garante que o vértice de origem existe no grafo
                    except ValueError:
                        # print(f"Coordenadas inválidas para vértice de origem: '{key_vertex_str}'. Pulando linha.")
                        continue

                    # Os elementos subsequentes são as arestas adjacentes
                    for i in range(1, len(parts)):
                        edge_str = parts[i]
                        edge_components = edge_str.split(",")
                        if len(edge_components) != 3:
                            continue
                        try:
                            end_lat = float(edge_components[0])
                            end_lon = float(edge_components[1])
                            weight = float(edge_components[2])
                            ending_vertex = Vertex(end_lat, end_lon)
                            rv.add_edge(key_vertex, GraphEdge(ending_vertex, weight))
                        except ValueError:
                            # print(f"Valores inválidos para aresta: '{edge_str}'. Pulando aresta.")
                            continue
            # print(f"Grafo carregado com sucesso de '{filename}'")
            return rv
        except FileNotFoundError:
            # print(f"Erro: Arquivo '{filename}' não encontrado.")
            return None
        except Exception as e:
            # print(f"Erro ao carregar o grafo de '{filename}': {e}")
            return None
