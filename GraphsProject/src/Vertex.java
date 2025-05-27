
public class Vertex {
	private double lat, lon;

	public Vertex(double latitude, double longitude) {
		this.lat = latitude;
		this.lon = longitude;
	}
	
	public Vertex() {
		// TODO Auto-generated constructor stub
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
	
	public String toString() {
		return (getLatitude() + "," + getLongitude());
	}
	
	@Override
	public boolean equals(Object obj) {
		if (this == obj) return true;
		if (obj == null || getClass() != obj.getClass()) return false;
		Vertex other = (Vertex) obj;
		return Double.compare(lat, other.lat) == 0 && Double.compare(lon, other.lon) == 0;
	}

	@Override
	public int hashCode() {
		return Double.hashCode(lat) * 31 + Double.hashCode(lon);
	}
	
}
