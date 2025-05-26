import java.util.ArrayList;

public class DocWay {
	private long id;
	ArrayList<Long> nodes;
	WayType type;
	
	public DocWay(long id, WayType type) {
		this.id = id;
		this.type = type;
		this.nodes = new ArrayList<Long>();
	}

	public ArrayList<Long> getNodes() {
		return nodes;
	}

	public void setNodes(ArrayList<Long> nodes) {
		this.nodes = nodes;
	}

	public WayType getType() {
		return type;
	}

	public void setType(WayType type) {
		this.type = type;
	}
	
	public void addNode(long nodeId) {
		nodes.add(nodeId);
	}
	
	public long getId() {
		return id;
	}
}
