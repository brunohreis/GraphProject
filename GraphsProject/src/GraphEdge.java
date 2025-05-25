public class GraphEdge {
	private Vertex ending;
	private double weight;
	public GraphEdge(Vertex ending, double weight) {
		this.ending = ending;
		this.weight = weight;
	}
	public double getWeight() {
		return weight;
	}
	public void setWeight(double weight) {
		this.weight = weight;
	}
	public Vertex getEnding() {
		return ending;
	}
	public void setEnding(Vertex ending) {
		this.ending = ending;
	}

}