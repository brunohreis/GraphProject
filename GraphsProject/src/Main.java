import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element; // Importar Element

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
// import java.util.Iterator; // Iterator não é usado diretamente aqui
import java.util.HashMap;
import java.util.LinkedList;

public class Main {

	public static void main(String[] args) {
		try {	
			File xmlFile = new File("maps/pca_liberdade.osm");
			HashMap<Long, DocNode> nodes = new HashMap<Long, DocNode>();
			LinkedList<DocWay> ways = new LinkedList<DocWay>();
			Graph graph = new Graph();

			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			DocumentBuilder builder = factory.newDocumentBuilder();
			Document document = builder.parse(xmlFile);
			document.getDocumentElement().normalize();

			System.out.println("Fazendo processamento do grafo");
			System.out.println("------------------------------------------------------------");

			fillNodesFromDocument(nodes, document);
			fillWaysFromDocument(nodes, ways, document);

			System.out.println("Processamento concluído");

			graph = buildGraph(nodes, ways);
			System.out.println("Vertices: " + graph.getvCount() + "\tEdges: " + graph.getEdgesCount());
			
			//exportVerticesToFile(graph, "graphs/vertices.txt");
			
			Vertex origin = graph.findVertex(-19.9255706, -43.9404899);
			Vertex destination = graph.findVertex(-19.9211485, -43.9339815);
			LinkedList<Edge> path = graph.getShortestPath(origin, destination);
			if(path != null) {
				double totalDistance = 0;
				int pathCounter = 1;
				for(Edge edge: path){
					double curDistance = edge.getEdge().getWeight();
					totalDistance += curDistance;
					System.out.println("Edge number " + pathCounter + ": " + curDistance + " m.");
				}
				System.out.println("Total distance: " + totalDistance);
			}
			else {
				System.out.println("There is no way between the chosen vertices.");
			}
			

		} catch (Exception e) {
			e.printStackTrace(); 
		}
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

	public static void exportVerticesToFile(Graph graph, String filename) {
		try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
			for (Vertex v : graph.getAdjacencyLists().keySet()) {
				writer.write(v.getLatitude() + ", " + v.getLongitude());
				writer.newLine();
			}
			System.out.println("Arquivo '" + filename + "' criado com sucesso.");
		} catch (IOException e) {
			System.err.println("Erro ao escrever no arquivo: " + e.getMessage());
		}
	}
}