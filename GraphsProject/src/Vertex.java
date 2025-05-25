
public class Vertex {
	private double lat, lon;

	public Vertex(double latitude, double longitude) {
		this.lat = latitude;
		this.lon = longitude;
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
