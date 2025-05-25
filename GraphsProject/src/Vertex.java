
public class Vertex {
	private long id;
	private double lat, lon;

	public Vertex(long id, double latitude, double longitude) {
		this.id = id;	
		this.lat = latitude;
		this.lon = longitude;
	}

	public long getId() {
		return id;
	}

	public double getLatitude() {
		return lat;
	}

	public void setLatitude(double latitude) {
		this.lat = latitude;
	}

	public double getLongitude() {
		return lon;
	}

	public void setLongitude(double longitude) {
		this.lon = longitude;
	}
	
}
