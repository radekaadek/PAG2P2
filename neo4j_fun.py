import osmnx as ox
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"  
NEO4J_PASSWORD = "pagosm123"  
NEO4J_USER = "neo4j"

def download_graph(city_name):
    print(f"Pobieranie grafu dla: {city_name}...")
    graph = ox.graph_from_place(city_name, network_type="drive")
    return graph

def insert_into_neo4j(graph):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Usuwanie rzeczy w bazie danych")

        for node, data in graph.nodes(data=True):
            session.run(
                """
                CREATE (n:Node {id: $id, x: $x, y: $y})
                """,
                id=node, x=data.get("x", 0), y=data.get("y", 0)
            )

        for u, v, data in graph.edges(data=True):
            session.run(
                """
                MATCH (a:Node {id: $u}), (b:Node {id: $v})
                CREATE (a)-[:ROAD {length: $length, highway: $highway}]->(b)
                """,\
                u=u, v=v, length=data.get("length", 0), highway=data.get("highway", "unknown")
            )
    
    print("Graf został zapisany w bazie danych")
    driver.close()

if __name__ == "__main__":
    city = "Warszawa, Polska"  
    graph = download_graph(city)
    insert_into_neo4j(graph)
