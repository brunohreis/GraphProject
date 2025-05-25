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
			neighbors = new LinkedList<GraphEdge>();
			adjacencyLists.put(beggining, neighbors);
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

	public void addVertex(Vertex vertex) {
		LinkedList<GraphEdge> adjList = new LinkedList<GraphEdge>();
		adjacencyLists.put(vertex, adjList);
		vCount++;
	}

	public int getEdgesCount() {
		int GraphEdgesCount = 0;
		for (HashMap.Entry<Vertex, LinkedList<GraphEdge>> entry : adjacencyLists.entrySet()) {
			LinkedList<GraphEdge> neighbors = entry.getValue();
			GraphEdgesCount += neighbors.size();
		}
		return GraphEdgesCount;
	}

	public LinkedList<Edge> getShortestPath(Vertex origin, Vertex destination) {
		HashMap<Vertex, Double> dist = new HashMap<Vertex, Double>(vCount);
		HashMap<Vertex, Vertex> pred = new HashMap<Vertex, Vertex>(vCount);
		ArrayList<Vertex> exp = new ArrayList<Vertex>();

		djikstra(origin, destination, dist, pred, exp);
		
		LinkedList<Edge> path = new LinkedList<>();
		Vertex current = destination;

		while (current != null && !current.equals(origin)) {
			Vertex prev = pred.get(current);
			if (prev == null) break; // Sem caminho

			Edge edge = getEdge(prev, current);
			if (edge != null) {
				path.addFirst(edge); // Adiciona no início, para construir na ordem correta
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
			Vertex toBeAdded = new Vertex();
			Vertex predecessor = new Vertex();
			for(int i=0; i<exp.size(); i++) {
				Vertex v = exp.get(i);
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
			dist.put(toBeAdded, minWeight);
			pred.put(toBeAdded, predecessor);
			exp.add(toBeAdded);
			counter++;
		}		
	}
}
