import java.util.ArrayList;

public class DocNode {
	private ArrayList<Long> ways;
	private long id;
	Vertex vertex;
	public DocNode(long id, Vertex vertex) {
		ways = new ArrayList<Long>();
		this.id = id;
		this.vertex = vertex;
	}
	public Vertex getVertex() {
		return vertex;
	}
	public void setVertex(Vertex vertex) {
		this.vertex = vertex;
	}
	public long getId() {
		return id;
	}
	public void setId(long id) {
		this.id = id;
	}
	public void addWay(long wayId) {
		ways.add(wayId);
	}
	public int getWaysLength() {
		return ways.size();
	}

}
