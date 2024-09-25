'''
Database access: You will write a few python functions organized in a 
few files like mysql_utils.py, mongodb_utils.py, and neo4j_utils.py to 
access the databases using their query languages via their network interfaces to support the widgets. 
'''
from neo4j import GraphDatabase


def sender():
    # Prompt user for Neo4j credentials
    '''
    you must have neo4j activated when running
    run using terminal prompt: python neo4j_utils.py
    then add password for your neo4j connection
    '''
    # User: enter your URI, username, and password here
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password1 = "neo4j_cs411"

    try:
        # Connect to Neo4j database
        driver = GraphDatabase.driver(uri, auth=(username, password1))
        # session = driver.session(database="academicworld")

        # # Execute Cypher query to retrieve data from academicworld database
        # result = session.run("MATCH (n) RETURN n LIMIT 10")

        # # Print query results
        # for record in result:
        #     print(record)

    except Exception as e:
        print("Error connecting to Neo4j database:", e)

    finally:
        if driver:
            return driver
        #     session.close()
        #     print("Neo4j session closed.")
        # if driver:
        #     driver.close()
        #     print("Neo4j driver closed.")


if __name__ == "__main__":
    sender()
