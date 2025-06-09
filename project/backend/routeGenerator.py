import os
import re
import networkx as nx
from math import radians, cos, sin, sqrt, atan2
from shapely.geometry import Point, LineString
from .graph import Vertex, GraphEdge, Graph

def extract_nodes_blocks(lines):
    blocks = []

    for i in range(len(lines)):
        # line = lines[i].strip()
        line = lines[i]
        if line.startswith("\t<node"):
            aux = line
            if not line.endswith("/>\n"):
                while not line.startswith("\t</node>"):
                    i += 1
                    # line = lines[i].strip()
                    line = lines[i]
                    aux += ";" + line
            blocks.append(aux)

    return blocks

def extract_ways_blocks(lines):
    blocks = []
    for i in range(len(lines)):
        # line = lines[i].strip()
        line = lines[i]
        if line.startswith("\t<way"):
            aux = line
            while not line.startswith("\t</way>"):
                i += 1
                # line = lines[i].strip()
                line = lines[i]
                aux += ";" + line
            blocks.append(aux)

    return blocks


def extract_blocks(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    ways = extract_ways_blocks(lines)
    nodes = extract_nodes_blocks(lines)

    return ways, nodes


def find_node_by_id(nodes, node_id):
    for node in nodes:
        if f"{node_id}" in node:
            return node
    return None


def find_way_by_id(ways, way_id):
    for way in ways:
        if f'id="{way_id}"' in way:
            return way
    return None


def get_node_coordinates(node):
    if isinstance(node, str):
        parts = node.split(";")
        for part in parts:
            if part.startswith("\t<node"):
                id = part[part.find("id=") + 4 : part.find("lat=") - 2]
                lat = part[part.find("lat=") + 5 : part.find("lon=") - 2]
                lon = part[part.find("lon=") + 5 : part.find("version") - 2]
                return id, lat, lon
    elif isinstance(node, tuple):
        id, lat, lon = node
        return id, lat, lon
    return None, None, None


def get_way_type(way_block):
    """
    Analisa o bloco de texto de uma 'way' para determinar seu tipo de sentido.
    Retorna 'ONE_WAY', 'REVERSED', ou 'BOTH_WAYS'.
    """
    # Procura por oneway="yes" ou junction="roundabout"
    if (
        '<tag k="oneway" v="yes"/>' in way_block
        or '<tag k="junction" v="roundabout"/>' in way_block
    ):
        return "ONE_WAY"
    # Procura por oneway="-1"
    elif '<tag k="oneway" v="-1"/>' in way_block:
        return "REVERSED"
    # O padrão é ser mão dupla
    else:
        return "BOTH_WAYS"
  
    
def normalize_ways(ways, default_way_type="BOTH_WAYS"):
    normalized = []
    for way in ways:
        if len(way) == 2:
            way_id, node_ids = way
            normalized.append((way_id, node_ids, default_way_type))
        elif len(way) == 3:
            normalized.append(way)
    return normalized


def extract_ways_from_blocks(ways):
    # Dicionário de categorias
    categories = {
        'useful_ways': [],
    }

    new_ways = ways.copy()
    rmv_qnt = 0

    # Mapeamento de palavras-chave para categorias
    keyword_to_category = {
        'trunk': 'useful_ways',
        'motorway': 'useful_ways',
        'living_street': 'useful_ways',
        'primary': 'useful_ways',
        'tertiary': 'useful_ways',
        'secondary': 'useful_ways',
        'residential': 'useful_ways',
    }

    for i in range(len(ways)):
        way = ways[i]
        matched_category = None

        for keyword, category in keyword_to_category.items():
            if f'<tag k="highway" v="{keyword}"/>' in way:
                matched_category = category
                break

        # Identificação do ID
        way_id = way[way.find('id=') + 4:way.find('version') - 2]

        # Extração dos nós
        nodes = []
        for part in way.split(';'):
            if '<nd ref=' in part:
                node_id = part[part.find('ref=') + 5:part.find('/>') - 1]
                nodes.append(node_id)

        # Adiciona à categoria correspondente
        if matched_category:
            if len(nodes) > 1:  # Verifica se há mais de um nó
                categories[matched_category].append((way_id, nodes))
        # else:
        #     categories['others'].append((way_id, nodes))

        new_ways.pop(i - rmv_qnt)
        rmv_qnt += 1

    categories['new_ways'] = new_ways
    return categories


def extract_nodes_from_blocks(nodes):
    aux_nodes = []
    relevant_nodes = []

    for i in range(len(nodes)):
        id, lat, lon = get_node_coordinates(nodes[i])
        if len(nodes[i].split(';')) == 1:
            aux_nodes.append((id, lat, lon))
        elif 'amenity' in nodes[i]:
            if 'drinking_water' not in nodes[i] and 'waste' not in nodes[i] and 'bicycle_parking' not in nodes[i] and 'fountain' not in nodes[i] and 'recycling' not in nodes[i] and 'bench' not in nodes[i] and 'water_point' not in nodes[i] and ' clock' not in nodes[i] and 'compressed_air' not in nodes[i] and 'parking_entrance' not in nodes[i] and 'water_point' not in nodes[i] and 'yes' not in nodes[i]:
                relevant_nodes.append((id, lat, lon))

    return aux_nodes, relevant_nodes


def create_kml_header():
    return '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'


def create_kml_footer():
    return "</Document>\n</kml>\n"


def create_kml_line_string(name, node_ids, nodes):
    kml_string = f"  <Placemark>\n    <name>{name}</name>\n    <LineString>\n      <coordinates>\n"
    for node_id in node_ids:
        node = find_node_by_id(nodes, node_id)
        if node is not None:
            id, lat, lon = get_node_coordinates(node)
            if lat and lon:
                kml_string += f"        {lon},{lat},0\n"
    kml_string += "      </coordinates>\n    </LineString>\n  </Placemark>\n"
    return kml_string


def create_kml_point(name, lat, lon):
    return f"  <Placemark>\n    <name>{name}</name>\n    <Point>\n      <coordinates>{lon},{lat},0</coordinates>\n    </Point>\n  </Placemark>\n"


def write_kml_ways(ways_by_category, nodes, output_file):
    with open(output_file, "w", encoding="utf-8") as kml_file:
        kml_file.write(create_kml_header())

        for category, ways in ways_by_category.items():
            kml_file.write(f"<Folder><name>{category}</name>\n")
            for way in ways:
                way_id, node_ids, _ = way
                kml_file.write(create_kml_line_string(way_id, node_ids, nodes))
            kml_file.write("</Folder>\n")

        kml_file.write(create_kml_footer())


def write_kml_nodes(
    nodes,
    relevant_nodes,
    output_file,
):
    with open(output_file, "w", encoding="utf-8") as kml_file:
        kml_file.write(create_kml_header())

        kml_file.write("<Folder><name>nodes</name>\n")
        for node in nodes:
            id, lat, lon = node
            kml_file.write(create_kml_point(id, lat, lon))
        kml_file.write("</Folder>\n")

        kml_file.write("<Folder><name>relevant_nodes</name>\n")
        for node in relevant_nodes:
            id, lat, lon = node
            kml_file.write(create_kml_point(id, lat, lon))
        kml_file.write("</Folder>\n")

        kml_file.write(create_kml_footer())


def useful_nodes(nodes, useful_ways):
    useful_nodes = []
    seen_ids = set()

    for way in useful_ways:
        node_ids = []
        if not isinstance(way, tuple) or len(way) < 2:
            continue  # ignora completamente formas inválidas
        elif len(way) == 2:
            _, node_ids = way
        elif len(way) == 3:
            _, node_ids, _ = way
        else:
            continue
        for node_id in node_ids:
            node = find_node_by_id(nodes, node_id)
            if node:
                id, lat, lon = get_node_coordinates(node)
                if id not in seen_ids:
                    useful_nodes.append((id, lat, lon))
                    seen_ids.add(id)
            # else:
                # print(f"Node with ID {node_id} not found in nodes list.")
    return useful_nodes


def projection(node, ways, nodes):
    smallest_dist = float("inf")
    closiest_way = None
    projected_point = None

    for way in ways:
        way_id, node_ids, way_type = way
        coords = []
        for node_id in node_ids:
            node_data = find_node_by_id(nodes, node_id)
            if node_data:
                id, lat, lon = get_node_coordinates(node_data)
                coords.append((float(lon), float(lat)))

        line = LineString(coords)
        point = Point(float(node[2]), float(node[1]))
        proj = line.interpolate(line.project(point))

        distance = point.distance(proj)
        if distance < smallest_dist:
            smallest_dist = distance
            closiest_way = way_id
            projected_point = proj

    return closiest_way, projected_point


def insertion_point(node, wayId, ways, nodes):
    insertion_point = None
    smallest_dist = float("inf")

    for way in ways:
        way_id, node_ids, way_type = way
        if way_id == wayId:
            if len(node_ids) > 2:
                for i in range(len(node_ids) - 1):
                    node1 = find_node_by_id(nodes, node_ids[i])
                    node2 = find_node_by_id(nodes, node_ids[i + 1])
                    if node1 and node2:
                        id1, lat1, lon1 = get_node_coordinates(node1)
                        id2, lat2, lon2 = get_node_coordinates(node2)
                        coord1 = (float(lon1), float(lat1))
                        coord2 = (float(lon2), float(lat2))
                        line = LineString([coord1, coord2])
                        point = Point(float(node[2]), float(node[1]))
                        proj = line.interpolate(line.project(point))
                        distance = point.distance(proj)

                        if distance < smallest_dist:
                            smallest_dist = distance
                            insertion_point = node_ids[i]
            else:
                insertion_point = node_ids[0]

            return insertion_point
    return insertion_point


def insertion_block(insertion_node_id, projection, insertion_point, wayId, ways, nodes):
    new_nodes = nodes.copy()
    new_ways = ways.copy()
    insert_lat = projection.y
    insert_lon = projection.x

    for i, node in enumerate(new_nodes):
        id, lat, lon = get_node_coordinates(node)
        if id == insertion_node_id:
            node = re.sub(r'lat="[^"]+"', f'lat="{insert_lat}"', node)
            node = re.sub(r'lon="[^"]+"', f'lon="{insert_lon}"', node)
            new_nodes[i] = node
            break

    for i, way in enumerate(new_ways):
        if not isinstance(way, tuple) or len(way) < 2:
            continue  # ignora completamente formas inválidas
        elif len(way) == 2:
            way_id, nodes_id = way
            way_type = "BOTH_WAYS"
        elif len(way) == 3:
            way_id, nodes_id, way_type = way
        else:
            continue  # ignora tuplas maiores que o esperado
        if way_id == wayId:
            new_nodes_id = nodes_id.copy()
            for j, node_ref in enumerate(new_nodes_id):
                if node_ref == insertion_point:
                    new_nodes_id.insert(j+1, insertion_node_id)
                    break
            new_ways[i] = (way_id, new_nodes_id)
            break

    return new_nodes, new_ways


def make_projections(relevant_nodes, ways, nodes):
    new_nodes = None
    new_ways = None

    for relevant_node in relevant_nodes:
        closiest_way, projected_point = projection(relevant_node, ways, nodes)
        insertion_point_id = insertion_point(
            relevant_node, closiest_way, ways, nodes)
        if new_nodes and new_ways:
            new_nodes, new_ways = insertion_block(relevant_node[0], projected_point,
                                                  insertion_point_id, closiest_way, new_ways, new_nodes)
        else:
            new_nodes, new_ways = insertion_block(relevant_node[0], projected_point,
                                                  insertion_point_id, closiest_way, ways, nodes)

    return new_nodes, new_ways


def write_final_kml_file(ways, nodes, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(create_kml_header())
        file.write("<Folder><name>Final Output</name>\n")

        file.write("<Folder><name>Ways</name>\n")
        for way in ways:
            way_id = 0
            node_ids = []
            if not isinstance(way, tuple) or len(way) < 2:
                continue  # ignora completamente formas inválidas
            elif len(way) == 2:
                way_id, node_ids = way
            elif len(way) == 3:
                way_id, node_ids, _ = way
            else:
                continue
            file.write(create_kml_line_string(way_id, node_ids, nodes))
        file.write("</Folder>\n")

        file.write("<Folder><name>Nodes</name>\n")
        for node in nodes:
            id, lat, lon = get_node_coordinates(node)
            file.write(create_kml_point(id, lat, lon))
        file.write("</Folder>\n")

        file.write("</Folder>\n")
        file.write(create_kml_footer())


def haversine(coord1, coord2):
    # Calcula distância entre dois pontos (lat, lon) em metros
    R = 6371000  # raio da Terra em metros
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)

    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def construir_grafo(nodes, ways):
    g = Graph()
    nodes_map = {node_id: Vertex(lat, lon) for node_id, lat, lon in nodes}

    for vertex in nodes_map.values():
        g.add_vertex(vertex)

    for way in ways:
        way_id = 0
        node_ids = []
        way_type = "BOTH_WAYS"
        if not isinstance(way, tuple) or len(way) < 2:
            continue  # ignora completamente formas inválidas
        elif len(way) == 2:
            way_id, node_ids = way
        elif len(way) == 3:
            way_id, node_ids, way_type = way
        else:
            continue
        for i in range(len(node_ids) - 1):
            id1, id2 = node_ids[i], node_ids[i + 1]
            vertex1, vertex2 = nodes_map.get(id1), nodes_map.get(id2)

            if vertex1 and vertex2:
                distance = haversine(
                    (vertex1.lat, vertex1.lon), (vertex2.lat, vertex2.lon)
                )

                if way_type == "ONE_WAY":
                    # Aresta apenas no sentido da via (1 -> 2)
                    g.add_edge(vertex1, GraphEdge(vertex2, distance))
                elif way_type == "REVERSED":
                    # Aresta apenas no sentido contrário da via (2 -> 1)
                    g.add_edge(vertex2, GraphEdge(vertex1, distance))
                else:
                    # Arestas em ambos os sentidos
                    g.add_edge(vertex1, GraphEdge(vertex2, distance))
                    g.add_edge(vertex2, GraphEdge(vertex1, distance))
                # ----------------------------------------------------

    return g, nodes_map


def minimum_path_kml(G, source, target, nodes, file_path):
    """Gera um arquivo kml com o menor caminho entre dois vértices de um grafo da biblioteca networkx (usado para teste)"""
    try:
        path = nx.shortest_path(G, source=source, target=target, weight="weight")
        kml_string = create_kml_line_string("Minimum Path", path, nodes)

        with open(file_path, "w", encoding="utf-8") as kml_file:
            kml_file.write(create_kml_header())
            kml_file.write(kml_string)
            kml_file.write(create_kml_footer())
    except nx.NetworkXNoPath:
        # print(f"Não há caminho entre {source} e {target}.")
        pass


def minimum_path_kml_custom(
    graph, nodes_map, source_id, target_id, nodes_data, file_path
):
    """Gera um arquivo kml com o menor caminho entre dois vértices de um grafo da classe Graph autoral"""
    source_vertex = nodes_map.get(source_id)
    target_vertex = nodes_map.get(target_id)

    if not source_vertex or not target_vertex:
        # print(f"Erro: Nó de origem ou destino não encontrado no mapeamento.")
        return

    path_edges = graph.get_shortest_path(source_vertex, target_vertex)

    if not path_edges:
        # print(f"Não há caminho entre {source_id} e {target_id}.")
        return

    # Constrói a lista de nós para o KML a partir das arestas
    path_node_ids = []
    # Encontra o ID do primeiro nó no caminho
    first_node_id = next(
        (node_id for node_id, v in nodes_map.items() if v == path_edges[0].beginning),
        None,
    )
    if first_node_id:
        path_node_ids.append(first_node_id)

    for edge in path_edges:
        # Encontra o ID do nó final de cada aresta
        node_id = next(
            (nid for nid, v in nodes_map.items() if v == edge.edge.ending_vertex), None
        )
        if node_id:
            path_node_ids.append(node_id)

    kml_string = create_kml_line_string("Minimum Path", path_node_ids, nodes_data)

    with open(file_path, "w", encoding="utf-8") as kml_file:
        kml_file.write(create_kml_header())
        kml_file.write(kml_string)
        kml_file.write(create_kml_footer())
    # print(f"Arquivo de caminho mínimo '{file_path}' gerado com sucesso.")

def extract_name(node):
    match = re.search(r'<tag k="name" v="([^"]+)"', node)
    if match:
        return match.group(1)
    return None


def extract_category(node):
    match = re.search(r'<tag k="amenity" v="([^"]+)"', node)
    if match:
        return match.group(1)
    return None


def extract_street(node):
    match = re.search(r'<tag k="addr:street" v="([^"]+)"', node)
    if match:
        return match.group(1)
    return None


def create_relevant_file(file_path, relevant_nodes, nodes):
    with open(file_path, 'w', encoding='utf-8') as file:

        for relevant_node in relevant_nodes:
            id, lat, lon = relevant_node
            node = find_node_by_id(nodes, id)
            name = extract_name(node)
            street = extract_street(node)
            category = extract_category(node)
            file.write(f'{id};{name};{street};{category}\n')


def generate_route(origin, destination):
    
    nodes = []
    nodes_map = {}
    
    graph = Graph()
    g_filename = 'project/rotas/graph.txt'
    if os.path.exists(g_filename) and os.path.getsize(g_filename) > 0:
        # Nesse caso, o grafo já foi pré-processado anteriormente e pode ser obtido de um arquivo de texto 
        graph = Graph.get_graph_from_file(filename=g_filename)

        # Carregar nodes_data e reconstruir nodes_map
        
        with open("project/rotas/nodes_data.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    node_id, lat, lon = parts
                    nodes.append((node_id, lat, lon))
                    nodes_map[node_id] = Vertex(lat, lon)
    else:
        # Caso contrário, o grafo precisa ser pré-processado

        arq_path = "project/rotas/desenvolvimento.osm"
        output_kml_allNodes = "project/rotas/all_nodes.kml"
        output_kml_ways = "ways.kml"

        ways, nodes = extract_blocks(arq_path)

        results_ways = extract_ways_from_blocks(ways)
        # Normaliza todas as tuplas para conter sempre 3 elementos
        for key in results_ways:
            results_ways[key] = normalize_ways(results_ways[key])

        # ways_by_category = {
        #     "Useful Ways": results_ways["useful_ways"],
        # }

        # write_kml_ways(ways_by_category, nodes, output_kml_ways)

        (
            others_nodes,
            relevant_nodes,  
        ) = extract_nodes_from_blocks(nodes)
        
        create_relevant_file("project/rotas/Relevant_index.csv", relevant_nodes, nodes)

        usefulNodes = useful_nodes(nodes, results_ways["useful_ways"])

        write_kml_nodes(
            others_nodes,
            relevant_nodes,
            output_kml_allNodes,
        )

        useful_ways = {
            "Useful Ways": results_ways["useful_ways"],
        }

        write_kml_ways(useful_ways, usefulNodes, "project/rotas/useful_ways.kml")

        write_final_kml_file(results_ways['useful_ways'],
                            usefulNodes, "project/rotas/final_output.kml")

        results_ways['useful_ways'] = normalize_ways(results_ways['useful_ways'])
        
        new_nodes, new_ways = make_projections(relevant_nodes, results_ways['useful_ways'], nodes)
        usefulNodes = useful_nodes(new_nodes, new_ways)

        write_final_kml_file(new_ways, usefulNodes,"project/rotas/final_output_with_projections.kml")

        graph, nodes_map = construir_grafo(usefulNodes, new_ways)
        graph.write_graph_to_file('project/rotas/graph.txt')

        # Salvar nodes_data
        with open("project/rotas/nodes_data.txt", "w") as f:
            for node_id, lat, lon in usefulNodes:
                f.write(f"{node_id},{lat},{lon}\n")

    # print(f"Grafo construído com {graph.num_nodes()} nós e {graph.num_edges()} arestas.")

    # Visualizar o grafo
    graph.save_image('project/rotas/graph.png')

    minimum_path_kml_custom(
        graph,
        nodes_map,
        source_id=origin,
        target_id=destination,
        nodes_data=nodes,
        file_path="project/rotas/minimum_path_custom.kml",
    )

# generate_route('324498040', '324498043')