import java.util.HashMap;
import java.util.LinkedList;

public class Graph {
	// The graph is represented in adjacency lists organized inside a hash map
	private HashMap<Long, LinkedList<Vertex>> adjacencyLists;
	private int vCount;
	
	Graph(int vCount){
		adjacencyLists = new HashMap<Long, LinkedList<Vertex>>(vCount); 
		this.vCount = vCount;
	}
	
	Graph() {
		adjacencyLists = new HashMap<Long, LinkedList<Vertex>>(); 
		vCount = 0;
	}
	
	public int getvCount() {
		return vCount;
	}

	public LinkedList<Vertex> getNeighbors(long id) {
		return adjacencyLists.get(id);
	}
	
	public void addEdge(Edge edge) {
		LinkedList<Vertex> neighbors = adjacencyLists.get(edge.getBeggining().getId());
		if(neighbors == null) {
			neighbors = new LinkedList<Vertex>();
			neighbors.add(edge.getBeggining());
			adjacencyLists.put(edge.getBeggining().getId(), neighbors);
		}
		neighbors.add(edge.getEnding());
	}
	
	public void addVertex(Vertex vertex) {
		LinkedList<Vertex> adjList = new LinkedList<Vertex>();
		adjList.add(vertex);
		adjacencyLists.put(vertex.getId(), adjList);
		vCount++;
	}
	
	public Vertex getVertex(long id) {
		return adjacencyLists.get(id).getFirst();
	}
	
	public int getEdgesCount() {
	    int edgesCount = 0;
	    for (HashMap.Entry<Long, LinkedList<Vertex>> entry : adjacencyLists.entrySet()) {
	        LinkedList<Vertex> neighbors = entry.getValue();
	        edgesCount += (neighbors.size() - 1); 
	    }
	    return edgesCount;
	}

}
