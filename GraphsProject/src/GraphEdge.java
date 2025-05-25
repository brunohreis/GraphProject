public class Edge {
	private Vertex beggining;
	private Vertex ending;
	private double weight;
	public Edge(Vertex beggining, Vertex ending, double weight) {
		this.beggining = beggining;
		this.ending = ending;
		this.weight = weight;
	}
	public double getWeight() {
		return weight;
	}
	public void setWeight(double weight) {
		this.weight = weight;
	}
	public Vertex getBeggining() {
		return beggining;
	}
	public void setBeggining(Vertex beggining) {
		this.beggining = beggining;
	}
	public Vertex getEnding() {
		return ending;
	}
	public void setEnding(Vertex ending) {
		this.ending = ending;
	}

}