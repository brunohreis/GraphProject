import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element; // Importar Element

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
// import java.util.Iterator; // Iterator não é usado diretamente aqui
import java.util.HashMap;
import java.util.LinkedList;

public class Main {

	public static void main(String[] args) {
		try {
			String gFilename = "graphs/graph2.txt";
			File graphFile = new File(gFilename);
			Graph graph = null;
			if (graphFile.length() == 0) {
				String mapFile = "maps/pca_liberdade.osm";
				graph = Graph.getGraphFromOSM(mapFile);
				graph.writeGraphToFile(gFilename);
			} else {
				System.out.println("Obtendo grafo a partir do arquivo " + gFilename);
				System.out.println("------------------------------------------------------------");
				graph = Graph.getGraphFromFile(gFilename);				
			}
			
			System.out.println("Graph totally built.");
			
			// Vertex from line 103
			Vertex origin = graph.findVertex(-10, -10); // -19.9210274, -43.9472383

			// Vertex from line 142
			Vertex destination = graph.findVertex(-10.2, -10.2); // -19.9287298, -43.929959

			if (origin != null && destination != null) {
				LinkedList<Edge> path = graph.getShortestPath(origin, destination);
				if (path != null) {
					double totalDistance = 0;
					int pathCounter = 1;
					for (Edge edge : path) {
						double curDistance = edge.getEdge().getWeight();
						totalDistance += curDistance;
						System.out.println("Edge number " + pathCounter + ": " + curDistance + " m.");
						pathCounter++;
					}
					System.out.println("Total distance: " + totalDistance);
				} else {
					System.out.println("There is no way between the chosen vertices.");
				}
			} else {
				System.out.println("Some of the vertices do not exist in the graph");
					}
			
//			ArrayList<Vertex> vertices = new ArrayList<>(graph.getAdjacencyLists().keySet());
//			
//			int succesCounter, errorCounter;
//			succesCounter = errorCounter = 0;
//			for(int i=0; i<vertices.size(); i++) {
//				Vertex origin = vertices.get(i);
//				for(int j=i+1; j!=i; j = (j+1)%vertices.size()) {
//					Vertex destination = vertices.get(j); 
//					if (origin != null && destination != null) {
//						LinkedList<Edge> path = graph.getShortestPath(origin, destination);
//						if (path != null) {
//							double totalDistance = 0;
//							int pathCounter = 1;
//							for (Edge edge : path) {
//								double curDistance = edge.getEdge().getWeight();
//								totalDistance += curDistance;
//							}
//							if(pathCounter > 1) {
//								System.out.println("Total distance: " + totalDistance);
//								succesCounter++;
//							}
//						} else {
//							//System.out.println("There is no way between the chosen vertices.");
//							errorCounter++;
//						}
//					} else {
//						//System.out.println("Some of the vertices do not exist in the graph");
//						errorCounter++;
//					}
//				}
//			}
//			System.out.println("Successfull runs: " + succesCounter);
//			System.out.println("Unsuccesfull runs " + errorCounter);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}


}