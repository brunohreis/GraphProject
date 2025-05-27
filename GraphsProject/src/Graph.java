import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Stack;

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
	
	public void writeGraphToFile(String filename) {
		try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
			for (Vertex v : getAdjacencyLists().keySet()) {
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
