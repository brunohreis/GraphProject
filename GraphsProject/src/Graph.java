import java.util.HashMap;
import java.util.LinkedList;

public class Graph {
	// The graph is represented in adjacency lists organized inside a hash map
	private HashMap<Vertex, LinkedList<Vertex>> adjacencyLists;
	private int vCount;
	
	Graph(int vCount){
		adjacencyLists = new HashMap<Vertex, LinkedList<Vertex>>(vCount); 
		this.vCount = vCount;
	}
	
	Graph() {
		adjacencyLists = new HashMap<Vertex, LinkedList<Vertex>>(); 
		vCount = 0;
	}
	
	public int getvCount() {
		return vCount;
	}

	public LinkedList<Vertex> getNeighbors(long id) {
		return adjacencyLists.get(id);
	}
	
	public void addEdge(Edge edge) {
		LinkedList<Vertex> neighbors = adjacencyLists.get(edge.getBeggining());
		if(neighbors == null) {
			neighbors = new LinkedList<Vertex>();
			adjacencyLists.put(edge.getBeggining(), neighbors);
		}
		neighbors.add(edge.getEnding());
	}
	
	public void addVertex(Vertex vertex) {
		LinkedList<Vertex> adjList = new LinkedList<Vertex>();
		adjacencyLists.put(vertex, adjList);
		vCount++;
	}
	
	public int getEdgesCount() {
	    int edgesCount = 0;
	    for (HashMap.Entry<Vertex, LinkedList<Vertex>> entry : adjacencyLists.entrySet()) {
	        LinkedList<Vertex> neighbors = entry.getValue();
	        edgesCount += neighbors.size();
	    }
	    return edgesCount;
	}
}
