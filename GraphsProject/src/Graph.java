import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Stack;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class Graph {
	// The graph is represented in adjacency lists organized inside a hash map
	private HashMap<Vertex, LinkedList<GraphEdge>> adjacencyLists;
	private int vCount;

	Graph(int vCount) {
		adjacencyLists = new HashMap<Vertex, LinkedList<GraphEdge>>(vCount);
		this.vCount = vCount;
	}

	Graph() {
		adjacencyLists = new HashMap<Vertex, LinkedList<GraphEdge>>();
		vCount = 0;
	}
	
	public static Graph getGraphFromOSM(String filename) throws ParserConfigurationException, SAXException, IOException {
		String mapPath = "maps/pca_liberdade.osm";
		File xmlFile = new File(mapPath);
		HashMap<Long, DocNode> nodes = new HashMap<Long, DocNode>();
		LinkedList<DocWay> ways = new LinkedList<DocWay>();

		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		Document document = builder.parse(xmlFile);
		document.getDocumentElement().normalize();

		System.out.println("Building graph through the map file " + mapPath);
		System.out.println("------------------------------------------------------------");

		fillNodesFromDocument(nodes, document);
		fillWaysFromDocument(nodes, ways, document);

		return buildGraph(nodes, ways);
	}
	
	private static Graph buildGraph(HashMap<Long, DocNode> nodesMap, LinkedList<DocWay> ways) {
		Graph graph = new Graph();
		for (int i = 0; i < ways.size(); i++) {
			int percent = (int) (((double) i / ways.size()) * 100);
			String bar = "=".repeat(percent / 2) + " ".repeat(50 - percent / 2);
			System.out.print("\rbuildGraph: [" + bar + "] " + i + "/" + ways.size() + "=" + percent + "%");
			System.out.flush();
			DocWay way = ways.get(i);
			ArrayList<Long> wayNodes = way.getNodes();
			if (wayNodes != null && wayNodes.size() > 0) {
				DocNode oldNode = nodesMap.get(wayNodes.get(0));
				DocNode newNode = null;
				// The first node from a way is always a vertex in the graph
				graph.addVertex(oldNode.getVertex());
				double edgeWeight = 0;
				double lastLat = oldNode.getVertex().getLatitude();
				double lastLon = oldNode.getVertex().getLongitude();
				for (int j = 1; j < wayNodes.size(); j++) {
					newNode = nodesMap.get(wayNodes.get(j));
					edgeWeight += haversineDistance(lastLat, lastLon, newNode.getVertex().getLatitude(),
							newNode.getVertex().getLongitude());
					if (newNode.getWaysLength() > 1 || j == wayNodes.size() - 1) {
						// The DocNode will only be a vertex in the graph if it remains to more than one
						// way (an intersection between streets) or if it is the last node in a way
						graph.addVertex(newNode.getVertex());
						if (way.getType() == WayType.ONE_WAY) {
							// if the street is one_way, there will be only a direct edge
							graph.addEdge(oldNode.getVertex(), new GraphEdge(newNode.getVertex(), edgeWeight));
						} else if (way.getType() == WayType.ONE_WAY_REVERSED) {
							// if the street is one_way_reversed, there will be only a reversed edge
							graph.addEdge(newNode.getVertex(), new GraphEdge(oldNode.getVertex(), edgeWeight));
						} else {
							// if the street is both_ways, there will be antiparallel edges
							graph.addEdge(oldNode.getVertex(), new GraphEdge(newNode.getVertex(), edgeWeight));
							graph.addEdge(newNode.getVertex(), new GraphEdge(oldNode.getVertex(), edgeWeight));
						}
						oldNode = newNode;
						edgeWeight = 0;
					}
					lastLat = newNode.getVertex().getLatitude();
					lastLon = newNode.getVertex().getLongitude();
				}
			}
		}
		System.out.println();
		return graph;
	}

	private static double haversineDistance(double lat1, double lon1, double lat2, double lon2) {
		double R = 6371000;
		double dLat = Math.toRadians(lat2 - lat1);
		double dLon = Math.toRadians(lon2 - lon1);
		double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(Math.toRadians(lat1))
				* Math.cos(Math.toRadians(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
		double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
		return R * c;
	}

	private static void fillNodesFromDocument(HashMap<Long, DocNode> nodes, Document document) {
		NodeList docNodes = document.getElementsByTagName("node");
		for (int i = 0; i < docNodes.getLength(); i++) {
			int percent = (int) (((double) i / docNodes.getLength()) * 100);
			String bar = "=".repeat(percent / 2) + " ".repeat(50 - percent / 2);
			System.out.print(
					"\rfillNodesFromDocument: [" + bar + "] " + i + "/" + docNodes.getLength() + "=" + percent + "%");
			System.out.flush();
			Node node = docNodes.item(i);
			if (node.getNodeType() == Node.ELEMENT_NODE) {
				Element nodeElement = (Element) node;
				long id = Long.parseLong(nodeElement.getAttribute("id"));
				double lat = Double.parseDouble(nodeElement.getAttribute("lat"));
				double lon = Double.parseDouble(nodeElement.getAttribute("lon"));
				nodes.put(id, new DocNode(id, new Vertex(lat, lon)));
			}
		}
		System.out.println();
	}

	private static void fillWaysFromDocument(HashMap<Long, DocNode> nodesMap, LinkedList<DocWay> ways,
			Document document) {
		NodeList docWays = document.getElementsByTagName("way");
		for (int i = 0; i < docWays.getLength(); i++) {
			int percent = (int) (((double) i / docWays.getLength()) * 100);
			String bar = "=".repeat(percent / 2) + " ".repeat(50 - percent / 2);
			System.out.print(
					"\rfillWaysFromDocument: [" + bar + "] " + i + "/" + docWays.getLength() + "=" + percent + "%");
			System.out.flush();
			Node way = docWays.item(i);
			if (way.getNodeType() == Node.ELEMENT_NODE) {
				Element wayElement = (Element) way;
				if (isValid(wayElement.getAttribute("highway"))) {
					long wayId = Long.parseLong(wayElement.getAttribute("id"));
					WayType type = getWayTypeFromAtts(wayElement.getAttribute("oneway"),
							wayElement.getAttribute("junction"));
					DocWay docWay = new DocWay(wayId, type);
					NodeList ndList = wayElement.getElementsByTagName("nd");
					for (int j = 0; j < ndList.getLength(); j++) {
						Node node = ndList.item(j);
						if (node.getNodeType() == Node.ELEMENT_NODE) {
							Element ndElement = (Element) node;
							long nodeId = Long.parseLong(ndElement.getAttribute("ref"));
							// The way at index of j is added to the list of ways that the node remains to
							DocNode docNode = nodesMap.get(nodeId);
							if (docNode != null) {
								docNode.addWay(wayId);
							}
							docWay.addNode(nodeId);
						}
					}
					// The way filled with its children is added to the ways list
					ways.add(docWay);
				}
			}
		}
		System.out.println();
	}

	// Checks if a way must be taken into consideration according to its highway
	// type
	private static boolean isValid(String attribute) {
		if (attribute.equals("footway") || attribute.equals("pedestrian") || attribute.equals("cycleway")
				|| attribute.equals("path") || attribute.equals("track") || attribute.equals("steps"))
			return false;
		else
			return true;
	}

	private static WayType getWayTypeFromAtts(String att1, String att2) {
		// att1: oneway, which may be "yes", "no" or "-1"
		// att2: junction, which can be "roundabout"
		WayType rv;
		if (att1.isEmpty() || att1.equals("no")) {
			rv = WayType.BOTH_WAYS;
		} else if (att1.equals("yes") || att2.equals("roundabout")) {
			rv = WayType.ONE_WAY;
		} else {
			rv = WayType.ONE_WAY_REVERSED;
		}
		return rv;
	}
	
	public void writeGraphToFile(String filename) {
		try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
			for (Vertex v : adjacencyLists.keySet()) {
				writer.write(v.toString() + ";");
				for(GraphEdge edge: adjacencyLists.get(v)) {
					writer.write(edge.toString() + ";");
				}
				writer.newLine();
			}
			System.out.println("Arquivo '" + filename + "' criado com sucesso.");
		} catch (IOException e) {
			System.err.println("Erro ao escrever no arquivo: " + e.getMessage());
		}
	}
	
	public static Graph getGraphFromFile(String filename) {
		Graph rv = new Graph();
		try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
			String line = reader.readLine();
			while(line != null) {
				String[] vertices = line.split(";");
				if(vertices.length > 0) {
					String[] keyVertexStr = vertices[0].split(",");
					if(keyVertexStr.length == 2) {
						double lat = Double.parseDouble(keyVertexStr[0]);
						double lon = Double.parseDouble(keyVertexStr[1]);
						Vertex keyVertex = new Vertex(lat, lon);
						rv.addVertex(keyVertex);
						for(int i=1; i<vertices.length; i++) {
							String[] vertexStr = vertices[i].split(",");
							if(vertexStr.length == 3) {
								lat = Double.parseDouble(vertexStr[0]);
								lon = Double.parseDouble(vertexStr[1]);
								Double weight = Double.parseDouble(vertexStr[2]);
								rv.addEdge(keyVertex, new GraphEdge(new Vertex(lat, lon), weight));
							}
						}
					}
				}
				line = reader.readLine();
			}
		} catch (IOException e) {
			System.err.println("Erro ao ler o arquivo: " + e.getMessage());
			return null;
		}
		return rv;
	}
	
	public HashMap<Vertex, LinkedList<GraphEdge>> getAdjacencyLists(){
		return adjacencyLists;
	}

	public int getvCount() {
		return vCount;
	}

	public LinkedList<GraphEdge> getNeighbors(Vertex v) {
		return adjacencyLists.get(v);
	}

	public void addEdge(Vertex beggining, GraphEdge GraphEdge) {
		LinkedList<GraphEdge> neighbors = adjacencyLists.get(beggining);
		if (neighbors == null) {
			neighbors = addVertex(beggining);
		}
		// Adds the ending vertex to the graph if it hasnt been added yet
	    if (!adjacencyLists.containsKey(GraphEdge.getEnding())) {
	        addVertex(GraphEdge.getEnding());
	    }
		neighbors.add(GraphEdge);
	}
	
	public Edge getEdge(Vertex v, Vertex w) {
		LinkedList<GraphEdge> neighbors = adjacencyLists.get(v);
		if(neighbors != null) {
			for(int i=0; i<neighbors.size(); i++) {
				GraphEdge edge = neighbors.get(i);
				if(edge.getEnding().equals(w)) {
					return new Edge(v, edge);
				}
			}
		}
		return null;
	}

	public LinkedList<GraphEdge> addVertex(Vertex vertex) {
		LinkedList<GraphEdge> adjList = new LinkedList<GraphEdge>();
		adjacencyLists.put(vertex, adjList);
		vCount++;
		return adjList;
	}

	public int getEdgesCount() {
		int GraphEdgesCount = 0;
		for (HashMap.Entry<Vertex, LinkedList<GraphEdge>> entry : adjacencyLists.entrySet()) {
			LinkedList<GraphEdge> neighbors = entry.getValue();
			GraphEdgesCount += neighbors.size();
		}
		return GraphEdgesCount;
	}
	
	public Vertex findVertex(double lat, double lon) {
	    for (Vertex v : adjacencyLists.keySet()) {
	        if (Math.abs(v.getLatitude() - lat) < 1e-7 && Math.abs(v.getLongitude() - lon) < 1e-7) {
	            return v;
	        }
	    }
	    return null;
	}

	public LinkedList<Edge> getShortestPath(Vertex origin, Vertex destination) {
		HashMap<Vertex, Double> dist = new HashMap<Vertex, Double>(vCount);
		HashMap<Vertex, Vertex> pred = new HashMap<Vertex, Vertex>(vCount);
		ArrayList<Vertex> exp = new ArrayList<Vertex>();

		djikstra(origin, destination, dist, pred, exp);
		
		if(dist.get(destination) == Double.MAX_VALUE) {
			return null;
		}
		
		LinkedList<Edge> path = new LinkedList<>();
		Vertex current = destination;

		while (current != null && !current.equals(origin)) {
			Vertex prev = pred.get(current);
			if (prev == null) break; 

			Edge edge = getEdge(prev, current);
			if (edge != null) {
				path.addFirst(edge); 
			}
			current = prev;
		}

		return path;
	}

	private void djikstra(Vertex origin, Vertex destination, HashMap<Vertex, Double> dist, HashMap<Vertex, Vertex> pred, ArrayList<Vertex> exp) {
		// Initialization
		for (Vertex v : adjacencyLists.keySet()) {
			// infinite distances
			dist.put(v, Double.MAX_VALUE);  
			// null predecessors
			pred.put(v, null);
		}
		// the origin's distance is 0
		dist.put(origin, (double) 0);
		// the first explored vertex is the origin
		exp.add(origin);
		
		int counter = 0;
		while(dist.get(destination) == Double.MAX_VALUE && counter < adjacencyLists.entrySet().size() - 1) {
			double minWeight = Double.MAX_VALUE;
			GraphEdge edge;
			Vertex toBeAdded, predecessor;
			toBeAdded = predecessor = null;
			for(int i=0; i<exp.size(); i++) {
				Vertex v = exp.get(i);
				if(adjacencyLists.containsKey(v)) {
					LinkedList<GraphEdge> neighbors = adjacencyLists.get(v); 
					for(int j=0; j<neighbors.size(); j++){
						edge = neighbors.get(j);
						Vertex w = edge.getEnding();
						if(!exp.contains(w) && ((dist.get(v) + edge.getWeight()) < minWeight)) {
							// if the vertex w has not been explored yet, the GraphEdge remains to the cut
							minWeight = dist.get(v) + edge.getWeight();
							toBeAdded = w;
							predecessor = v;
						}
					}
				}
				else {
					System.out.println("Map doesnt have the key");
				}
				
			}
			if(toBeAdded != null) {
				dist.put(toBeAdded, minWeight);
				pred.put(toBeAdded, predecessor);
				exp.add(toBeAdded);
				counter++;
			}
			else {
				break;
			}
		}		
	}
}
