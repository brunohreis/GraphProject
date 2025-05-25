import java.util.ArrayList;

public class DocNode {
	private ArrayList<Long> ways;
	Vertex vertex;
	public DocNode(Vertex vertex) {
		ways = new ArrayList<Long>();
		this.vertex = vertex;
	}
	public Vertex getVertex() {
		return vertex;
	}
	public void setVertex(Vertex vertex) {
		this.vertex = vertex;
	}
	public void addWay(long wayId) {
		ways.add(wayId);
	}
	public int getWaysLength() {
		return ways.size();
	}

}
