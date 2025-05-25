
public class Edge {
	private Vertex beggining;
	private GraphEdge edge;
	public Edge(Vertex beggining, GraphEdge edge) {
		this.beggining = beggining;
		this.edge = edge;
	}
	public Vertex getBeggining() {
		return beggining;
	}
	public void setBeggining(Vertex beggining) {
		this.beggining = beggining;
	}
	public GraphEdge getEdge() {
		return edge;
	}
	public void setEdge(GraphEdge edge) {
		this.edge = edge;
	}
	
}
