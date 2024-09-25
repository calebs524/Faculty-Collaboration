from mysql.connector import errorcode
import mysql.connector
import mongodb_utils
from neo4j import GraphDatabase
import neo4j_utils
import pandas as pd
import matplotlib.pyplot as plt
import mysql_utils1
import neo4j_utils
import networkx as nx


'''
goal: use matplotlib to create a graph
this graph will show the number of publications for the given keyword
we will use sql to make a query and output this into a graph
'''


def helper(keyword):
    connection = mysql_utils1.connect_to_mysql()
    if connection:
        print("it works")
        cursor = connection.cursor()
        '''
        here, we can create a query that shows the number of the publications vs the graph
        '''
        query = "SELECT year, COUNT(p.id) AS num " \
            "FROM publication p " \
            "JOIN publication_keyword pk ON p.id = pk.publication_id " \
            "JOIN keyword k ON k.id = pk.keyword_id " \
            "WHERE k.name = %s " \
            "GROUP BY year " \
            "ORDER BY year"

        cursor.execute(query, (keyword,))
        result = cursor.fetchall()
        # for row in data:
        #     print(row)
        df = pd.DataFrame(result, columns=['year', 'num_publications'])
        df['year'] = df['year'].fillna(0).astype(
            int)   # Convert year to integer

        # # Determine the full range of years from min to max
        year_range = range(df['year'].min(), df['year'].max() + 1)

        # # Create a DataFrame that represents all years in the range with default publications count of 0
        df_full = pd.DataFrame(list(year_range), columns=['year'])
        df_full['num_publications'] = 0
        df_final = pd.merge(df_full, df, on='year', how='outer').fillna(0)
        df_final.drop("num_publications_x", axis=1,  inplace=True)
        df_final['num_publications_y'] = df_final['num_publications_y'].astype(
            int)
        df_final.rename(
            columns={"num_publications_y": "num_publications"}, inplace=True)
        # # Display the final DataFrame
        # print(df_final)
        return df_final


def helper2(university):
    driver = neo4j_utils.sender()
    connection = driver.session(database="academicworld")
    if connection:
        print("it works")

        '''
        here, we can create a query that shows the number of the publications for a university over time
        '''
        query = "MATCH (i:INSTITUTE{name:$university})"\
            "<-[:AFFILIATION_WITH]-(:FACULTY)-[:PUBLISH]->(p:PUBLICATION)"\
            "RETURN p.year AS Year, COUNT(p) AS NumberOfPublications ORDER BY Year"
        result = connection.run(query, {"university": university})
        df = pd.DataFrame(result, columns=['year', 'num_publications'])
        df = df.drop(0)
        df['year'] = df['year'].astype(int)  # Convert year to integer

        # # Determine the full range of years from min to max
        year_range = range(df['year'].min(), df['year'].max() + 1)

        # # Create a DataFrame that represents all years in the range with default publications count of 0
        df_full = pd.DataFrame(list(year_range), columns=['year'])
        df_full['num_publications'] = 0
        df_final = pd.merge(df_full, df, on='year', how='outer').fillna(0)
        df_final.drop("num_publications_x", axis=1,  inplace=True)
        df_final['num_publications_y'] = df_final['num_publications_y'].astype(
            int)
        df_final.rename(
            columns={"num_publications_y": "num_publications"}, inplace=True)
        # # Display the final DataFrame
        # print(df_final)
        connection.close()
        driver.close()
        print(df_final)
        return df_final


def create_graph_from_query(session, query):
    result = session.run(query)
    graph = nx.Graph()
    nodes = []
    edges = []

    for record in result:
        path = record['p']
        for i, node in enumerate(path.nodes):
            # print(node)
            properties = dict(node.items())
            # print(list(node.labels)[0])
            properties['type'] = list(node.labels)[0]
            if 'id' in properties:
                nodes.append((i, properties))
        for i, rel in enumerate(path.relationships):
            # print(rel)
            properties = dict(rel.items())
            properties['type'] = rel.type
            properties['id'] = rel.element_id.split(':')[-1]
            if 'type':
                edges.append((i, i+1, properties))
    for node in nodes:
        graph.add_node(node[0], **node[1])
    for edge in edges:
        graph.add_edge(edge[0], edge[1], **edge[2])
    return graph


def collaborator(c1_name, c2_name):
    mysqlconnection = mysql_utils1.connect_to_mysql()
    cursor = mysqlconnection.cursor()

    driver = neo4j_utils.sender()
    connection = driver.session(database="academicworld")
    df = pd.DataFrame(columns=[
        'from_name',
        'from_id',
        'from_type',
        'to_name',
        'to_id',
        'to_type',
        'rel_type',
        'rel_score',
        'rel_id',
        'rel_def'
    ])
    if connection:
        print("it works")
        # c1_name = "Jiawei Han"
        # c2_name = "William Freeman"

        query = (
            "MATCH "
            "(c1:FACULTY {name: $c1}), "
            "(c2:FACULTY {name: $c2}), "
            "p = shortestPath((c1)-[*]-(c2)) "
            "RETURN p "
            "LIMIT 1"
        )

        formatted_query = query.replace(
            "$c1", f'"{c1_name}"').replace("$c2", f'"{c2_name}"')
        print(formatted_query)
        result = connection.run(formatted_query)
        result_graph = create_graph_from_query(connection, formatted_query)
        print(result_graph.nodes(data=True))  # Print nodes with properties
        print(result_graph.edges(data=True))

        edges_list = list(result_graph.edges(data=True))
        # print(edges_list)
        for i, edge in enumerate(edges_list):
            # print(edge)
            from_v = result_graph.nodes[edge[0]]
            to_v = result_graph.nodes[edge[1]]
            prop = edge[2]
            # print(from_v['id'], from_v['type'], to_v['id'], to_v['type'])
            fName = ""
            if (from_v['type'] == "PUBLICATION"):
                fName = from_v['title']
            else:
                fName = from_v['name']
            tName = ""
            if (to_v['type'] == "PUBLICATION"):
                tName = to_v['title']
            else:
                tName = to_v['name']
            rScore = 0
            if prop['type'] in ("AFFILIATION_WITH", "PUBLISH"):
                rScore = 0
            else:
                rScore = prop['score']
            r_def = (from_v['id'], to_v['id'], prop['id'])
            row_data = {
                'from_name': fName,
                'from_id': from_v['id'],
                'from_type': from_v['type'],
                'to_name': tName,
                'to_id': to_v['id'],
                'to_type': to_v['type'],
                'rel_type': prop['type'],
                'rel_score': rScore,
                'rel_id': prop['id'],
                'rel_def': r_def
            }

            # # Insert the row into the DataFrame
            df.loc[len(df)] = row_data
        pd.set_option('display.max_columns', None)

        # print(df)
        rel_def_list = df['rel_def'].tolist()

        from_id = int(df['from_id'].iloc[0][1:])  # Accessing the first element
        to_id = int(df['to_id'].iloc[-1][1:])
        stringified_data = [
            '(' + ', '.join(map(str, tup)) + ')' for tup in rel_def_list]

        result_string = '[' + ', '.join(stringified_data) + ']'

        # print(result_string)

        query2 = f"INSERT INTO collaborator_path (faculty1_id, faculty2_id, Path) VALUES ({from_id}, {to_id}, '{result_string}')"

        print(query2)

        cursor.execute(query2)
        mysqlconnection.commit()
        cursor.close()
        mysqlconnection.close()
        # print(df)
        return df

        # Call the function


def rel_explainer(df):
    relations = "Relation: "
    try:
        for index, row in df.iterrows():
            # print("Row data:", row)
            rel_type = row['rel_type']
            if rel_type == "AFFILIATION_WITH":
                t1 = ""
                if row['from_type'] == "FACULTY":
                    t1 = row["from_name"] + \
                        " is affiliated with " + row["to_name"] + '. '
                    # print(t1)
                else:
                    t1 = row["to_name"] + \
                        " is affiliated with " + row["from_name"] + '. '
                    # print(t1)
                relations += t1 + '\n'
                # print(t1)

            elif rel_type == "INTERESTED_IN":
                t1 = ""
                if row['from_type'] == "FACULTY":
                    t1 = row["from_name"] + " is interested in " + \
                        row["to_name"] + " with a score of " + \
                        str(row['rel_score']) + '. '
                else:
                    t1 = row["to_name"] + " is interested in " + \
                        row["from_name"] + " with a score of " + \
                        str(row['rel_score']) + '. '
                relations += t1 + '\n'
                # print(t1)

            elif rel_type == "LABEL_BY":
                t1 = ""
                if row['from_type'] == "PUBLICATION":
                    t1 = "\"" + row["from_name"] + "\" is labeled by " + \
                        row["to_name"] + " with a score of " + \
                        str(row['rel_score']) + '. '
                else:
                    t1 = "\"" + row["to_name"] + "\" is labeled by " + \
                        row["from_name"] + " with a score of " + \
                        str(row['rel_score']) + '. '
                relations += t1 + '\n'
                # print(t1)

            elif rel_type == "PUBLISH":
                t1 = ""
                if row['from_type'] == "FACULTY":
                    t1 = row["from_name"] + \
                        " published \"" + row["to_name"] + '\". '
                else:
                    t1 = row["to_name"] + " published \"" + \
                        row["from_name"] + '\". '
                relations += t1 + '\n'
                # print(t1)
    except Exception as e:
        print("An error occurred:", e)
    #     # You can add additional handling or logging here if needed
    return relations


def findProfs(university, keyword):
    # next, find all possible professors related to that
    client = mongodb_utils.connect_to_mongodb()
    if client:
        db = client['academicworld']

        query = [
            {"$match": {"affiliation.name": university}},
            {"$unwind": "$keywords"},
            {"$match": {"keywords.name": keyword}},
            {"$group": {"_id": {"id": "$id", "name": "$name"}}},
            {"$project": {"_id": "$_id.id", "name": "$_id.name"}}
        ]

        results = db.faculty.aggregate(query)
        # print("run query")
        # print((results))
        if not (results.alive):
            print("no available professors, please search again")
            return None
        else:
            names_list = [result["name"] for result in results]
            print(names_list)

            names_string = '\"' + '\" \"'.join(names_list) + '\"'

            print(names_string)
            return names_string


if __name__ == "__main__":
    mysqlconnection = mysql_utils1.connect_to_mysql()
    cursor = mysqlconnection.cursor()
    query = "INSERT INTO collaborator_path (faculty1_id, faculty2_id, Path) VALUES (657, 2300, '[(f657, p2788920170, 672586), (p2788920170, k406, 3855783), (k406, f2300, 192716)]')"
    cursor.execute(query)
    mysqlconnection.commit()

    # findProfs("Carnegie Mellon University", "internet")
    # finder("Massachusetts Institute of Technology", "internet")
    # collaborator("Jiawei Han", "William Freeman")
    # table_creator()
    # connection = mysql_utils1.connect_to_mysql()
    # cursor = connection.cursor()
    # cursor.execute("select * from collaborator_path;")

    # # do this entire part before calling the function

    # query = "SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = 'academicworld'   AND table_name = 'faculty'   AND index_name = 'idx_name';"
    # cursor.execute(query)
    # r = cursor.fetchall()
    # if r is not None and r[0][0] > 0:
    #     print("The idx_name view exists.")
    # else:
    #     cursor.execute("CREATE INDEX idx_name ON faculty (name);")

    # name_checker = "SELECT COUNT(name) from FACULTY where name = %s;"
    # cursor.execute(name_checker, (c1_name,))
    # r = cursor.fetchall()
    # if r is not None and r[0][0] == 0:
    #     print(f"The name {c1_name} does not exist")

    # cursor.execute(name_checker, (c2_name,))
    # r = cursor.fetchall()
    # if r is not None and r[0][0] == 0:
    #     print(f"The name {c2_name} does not exist")

    # # this part


def finder(university, keyword):
    # first, check if university and keyword are valid
    # we create views for both the university and the keyword
    view_creator = "CREATE VIEW university_names AS SELECT name FROM university;"
    view_checker = "SELECT COUNT(*) AS view_exists FROM information_schema.views " \
        "WHERE table_schema = %s AND table_name = %s"
    connection = mysql_utils1.connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            view_checker, ('academicworld',  'university_names'))
        result = cursor.fetchall()
        if result is not None and result[0][0] > 0:
            print("The university_names view exists.")
        else:
            cursor.execute(view_creator)

    view_creator2 = "CREATE VIEW keyword_names AS SELECT name FROM keyword;"
    view_checker2 = "SELECT COUNT(*) AS view_exists FROM information_schema.views " \
        "WHERE table_schema = %s AND table_name = %s"
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            view_checker2, ('academicworld',  'keyword_names'))
        result = cursor.fetchall()
        if result is not None and result[0][0] > 0:
            print("The keyword_names view exists.")
        else:
            cursor.execute(view_creator2)
    # now, we check views to ensure they exist:
    uni_checker = "SELECT COUNT(*) from university_names where name = %s"
    key_checker = "SELECT COUNT(*) from keyword_names where name = %s"
    if connection:
        cursor = connection.cursor()
        cursor.execute(uni_checker, (university,))
        result = cursor.fetchall()
        print(result)
        if result is not None and result[0][0] > 0:
            print(f"{university}  exists.")
        else:
            print(f"{university} does not exists.")

        cursor.execute(key_checker, (keyword,))
        result = cursor.fetchall()
        print(result)
        if result is not None and result[0][0] > 0:
            print(f"{keyword}  exists.")
        else:
            print(f"{keyword} does not exists.")

    # next, find all possible professors related to that
    client = mongodb_utils.connect_to_mongodb()
    if client:
        db = client['academicworld']

        query = [
            {"$match": {"affiliation.name": university}},
            {"$unwind": "$keywords"},
            {"$match": {"keywords.name": keyword}},
            {"$group": {"_id": {"id": "$id", "name": "$name"}}},
            {"$project": {"_id": "$_id.id", "name": "$_id.name"}}
        ]

        results = db.faculty.aggregate(query)
        for result in results:
            print(result)

    # for record in result:
    #     path = record['p']
    #     nodes = path.nodes
    #     for i, node in enumerate(nodes):
    #         # print(node)
    #         properties = dict(node.items())
    #         graph.add_node(i, **properties)
    #         if i > 0:
    #             prev_node = path.nodes[i-1]
    #             properties = dict(path.relationships[i-1].items())
    #             print(properties)
    #             end_node_properties = dict(prev_node.items())
    #             graph.add_edge(i-1, i, **properties)
    # return graph


'''
      mongodb query:
        db.publications.aggregate([
    {
        $match: {
            "keywords.name": "skill"  // Adjust "skill" to your target keyword
        }
    },
    {
        $group: {
            _id: "$year",  // Group by the "year" field
            numberOfPublications: { $sum: 1 }  // Count publications per year
        }
    },
    {
        $sort: {
            _id: 1  // Sort by year (ascending)
        }
    }
]);

neo4j query: MATCH (:KEYWORD {name: "skill"})<-[LABEL_BY]-(p:PUBLICATION)
        RETURN p.year AS PublicationYear, COUNT(p) AS NumberOfPublications
        ORDER BY p.year
        Started streaming 39 records after 3 ms and completed after 19 ms.

'''

# def table_creator():
#     # Connect to MySQL
#     connection = mysql_utils1.connect_to_mysql()

#     if connection:
#         cursor = connection.cursor()

#         # Check if the table exists
#         # Check if the table exists
#         cursor.execute("SHOW TABLES LIKE 'collaborator_path'")
#         table_exists = cursor.fetchone()

#         # If the table doesn't exist, create it
#         if not table_exists:
#             cursor.execute("""
#                     CREATE TABLE `academicworld`.`collaborator_path` (
#                       `faculty1_id` INT NOT NULL,
#                       `faculty2_id` INT NOT NULL,
#                       `Path` VARCHAR(512) NULL,
#                       INDEX `id_idx2` (`faculty2_id` ASC) INVISIBLE,
#                       PRIMARY KEY (`faculty1_id`, `faculty2_id`),
#                       INDEX `id_idx1` (`faculty1_id` ASC) VISIBLE,
#                       CONSTRAINT `f_id1`
#                         FOREIGN KEY (`faculty1_id`)
#                         REFERENCES `academicworld`.`faculty` (`id`)
#                         ON DELETE CASCADE
#                         ON UPDATE CASCADE,
#                       CONSTRAINT `f_id2`
#                         FOREIGN KEY (`faculty2_id`)
#                         REFERENCES `academicworld`.`faculty` (`id`)
#                         ON DELETE CASCADE
#                         ON UPDATE CASCADE);
#                 """)

#         # Check if the trigger before_insert_check_duplicates exists
#         cursor.execute(
#             "SHOW TRIGGERS LIKE 'before_insert_check_duplicates'")
#         trigger_exists = cursor.fetchall()

#         # If the trigger doesn't exist, create it
#         if not trigger_exists:
#             cursor.execute("""

#                     DELIMITER $$
#                     USE `academicworld`$$
#                     CREATE DEFINER = CURRENT_USER TRIGGER before_insert_check_duplicates
#                     BEFORE INSERT ON `collaborator_path`
#                     FOR EACH ROW
#                     BEGIN
#                         DECLARE duplicate_count INT;

#                         -- Check if the combination of faculty1_id and faculty2_id already exists
#                         SELECT COUNT(*) INTO duplicate_count
#                         FROM collaborator_path
#                         WHERE (faculty1_id = NEW.faculty1_id AND faculty2_id = NEW.faculty2_id)
#                            OR (faculty1_id = NEW.faculty2_id AND faculty2_id = NEW.faculty1_id);

#                         -- If the combination already exists, raise an error
#                         IF duplicate_count > 0 THEN
#                             SET NEW = NULL;
#                         END IF;
#                     END$$
#                     DELIMITER ;
#                 """)
#         else:
#             print("t1 exists")

#         # Check if the trigger before_insert_check_faculty_existence exists
#         cursor.execute("SHOW TRIGGERS LIKE 'before_insert_check_faculty_existence'")
#         trigger_exists = cursor.fetchall()

#         # If the trigger doesn't exist, create it
#         if not trigger_exists:
#             cursor.execute("""
#                     DROP TRIGGER IF EXISTS `academicworld`.`before_insert_check_faculty_existence`;

#                     DELIMITER $$
#                     USE `academicworld`$$
#                     CREATE DEFINER = CURRENT_USER TRIGGER before_insert_check_faculty_existence
#                     BEFORE INSERT ON `collaborator_path`
#                     FOR EACH ROW
#                     BEGIN
#                         DECLARE faculty1_exists INT;
#                         DECLARE faculty2_exists INT;

#                         -- Check if faculty1_id exists in the faculty table
#                         SELECT COUNT(*) INTO faculty1_exists
#                         FROM faculty
#                         WHERE id = NEW.faculty1_id;

#                         -- Check if faculty2_id exists in the faculty table
#                         SELECT COUNT(*) INTO faculty2_exists
#                         FROM faculty
#                         WHERE id = NEW.faculty2_id;

#                         -- If either faculty1_id or faculty2_id does not exist, reject the change
#                         IF faculty1_exists = 0 OR faculty2_exists = 0 THEN
#                             SET NEW = NULL;
#                         END IF;
#                     END$$
#                     DELIMITER ;
#                 """)
#         else:
#             print("t2 exists")

#         # Commit the changes
#         connection.commit()
#         print("Table and triggers created successfully")

#         cursor.close()
#         connection.close()
