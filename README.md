**CS 411 Final Project**

*By*: Caleb Satvedi and Saswati Munshi<br>

**Title**: Facutly Collaboration Network<br>

**Purpose**: What is the application scenario? Who are the target users? What are the objectives?<br>

The application scenario is for faculty members and prospective researchers to learn about what the market is for various research topics given the keywords available. The target users include current faculty members, undergraduate/graduate researchers, and university executives looking to employ these researchers. The objectives are to help the target audience learn about the hottest research topics currently, others who are interested in the same research topics, and help them get in contact with them.<br>

**Demo**: Give the link to your video demo. Read the video demo section below to understand what contents are expected in your demo.<br>
https://mediaspace.illinois.edu/media/t/1_1kjch74z

**Installation**: How to install the application? You don’t need to include instructions on how to install and initially populate the databases if you only use the given dataset. <br>

No additional installation necessary.<br>

**Usage**: How to use it? <br>
1. Turn on your neo4j server for academic work
2. Enter your mysql username and password between lines 10 and 17 in file mysql_utils1.py


3. Enter your neo4j URI, username, and password between lines 17-19 in neo4j_utils.py

   

4. Run python app.py in terminal.<br>

**Design**: What is the design of the application? Overall architecture and components.<br> 
The design of this application is built around the databases and the presentation of data to the user.<br>
For the architechture, we built three tiers: presentation, application, and data tier. The presentation tier is lodged in app.py, which holds the front-end designs for the widgets. The application tier is both in app.py and graph_creator.py, and holds the logic for querying the databases as well as building the framework and output that would presented in the application tier. The data tier is housed in the mysql_tables.py, mysql_utils1.py, neo4j_utils.py, and mongodb_utils.py. These files hold the connections to their respective databases, and create the necesary tables and configurations for the back end of this application.<br>
The components of this design rely on the databases we used. We built around the strengths of each database in terms of speed and whats they're used for given the classroom knowledge. For example, we learned about how Neo4J is a graph database, so we used Neo4j to create graph mappings between the different nodes. We also learned about how MongoDB is a document based database, so we played to the strength of that by implementing filtering and document searching via MongoDB. We used MYSQL for storing user information, as well as querying the database for relational information.<br>
We also used common python libraries such as pandas to sift the queried data and organize them for presentation use. On the presentation side, those components include the dash imports, such as html and dcc for web formatting the data, Input, Output, and State dependencies for stable communication between server and client, and visualization tools such as dash_table, DataTable, and plotly_express for displaying and graphing data metrics.
<br>

**Implementation**: 
 In this project, we leverage several libraries and tools to streamline our application. Here are the key libraries and tools we are using: <br>

* MongoDB/ pymongo: In order to utilize the mongodb database, we use the pymongo library to create that connection. Then, we are able to pass that client connection to the functionalities to query and retrieve the data that we need. <br>
* Neo4j: The neo4j library is used to connect and interact with Neo4j database. We pass around the driver to the various functionalities for querying and retrieving the data with a connected session to the academic world database, and then close out the session and driver when it's no longer in use. <br>
* MySQL: We employ the mysql.connector library to interact with MySQL. We create and then pass around the connection to the functions, which create a cursor to query the academic world database. Additionally, we use the commit functionality when transacting to/from the database. We also have built various table to house user data. <br>
* NetworkX: The networkx library is used in graph_creator.py. It's used to create a python graph object, which is populated with the nodes and edges in the relationship between the two facutly members. This is specific to the "Find Your Match" widget. With this graph, we can easily store the relationships between the various nodes that are used to connect these two faculty members. You can find this in lines 98-124 of graph_creator.py, function create_graph_from_query. <br>
* Plotly Express: We used Plotly Express to create various graphs, such as the Favorite Keyword Trend graph, University Publications by Year, and Publications by Year for Keywords for our widgets.
* Pandas: The pandas library is used for data manipulation and to convert the data we retrive from the database into a DataFrame with specified column names. We used this for Find your match dashboard  <br>
* Flask's request Module: The Flask request module allows access to request-specific information during an HTTP request, such as the client's IP address (request.remote_addr). We are using this to create unique user table for Favorite Keyword Dashboard. <br>
* Socket Library: It imports the socket module and then uses socket.gethostbyname(socket.gethostname()) to obtain the IP address. <br>
socket.gethostname() returns the hostname of the local machine, and socket.gethostbyname() resolves this hostname to obtain the corresponding IP address. We are using this to create unique user table for Favorite Keyword Dashboard.  <br>

**Database Techniques**: What database techniques have you implemented? How? 

***Indexing:***
* We created indexes for the keyword name and the faculty name for the "Find Your Match" widget. We used these indexes in order to determine whether or not the inputted faculty names and keywords the users gave us existed or not, and by using these indexes, we could make those determinations faster. Find this in lines 404-411 and 443-449 of app.py.<br>
***Views:***
* We created a view for the names of the university. We used this view in the "Find Your Match" widget, specifically the drop down menu for being able to select the university names. Find this in lines 119-131 of mysql_tables.py.<br>
***Constraint:***
* We used constraints when created the collaborator_path table. The specific constraints we used were in creating the facutly_id1 and faculty_id2 attributes to be a foreign key to reference the id attribute of the faculty table. This allowed us to create the condition to cascade on both delete and update. This table would be used for the Find Your Match widget, so if a faculty id is changed or deleted, we can then change or delete that row of the table to keep up with the changes in the database. Find this in lines 22-31 of mysql_tables.py.<br>
* Also we utilized the primary key constraint on the 'keyword' column when creating the table user_favkeyword.  Find this in lines 75-80 of app.py.<br>

***Triggers:***
* We created 3 triggers for the collaborator_path table(above). The first trigger we created was the before_insert_check_duplicates, which would check if both faculty member's id's are already in the table. We did this to make sure that the table wouldn't be populated with the same combination of those faculty member's ids multiple times. If it is, then we will reject the row addition and throw an error, stating that the combination of those faculty member's ids are already present in the table. Find this in lines 44-68 of mysql_tables.py. <br>
* The next trigger we created was before_insert_check_faculty_existence, which checked if both faculty members existed in the faculty table, and rejected the change if they weren't. We did this to make sure that we are inputting current faculty members into the table, and rejecting those who are not faculty members anymore. If a user inputs faculty members who are not in the table, the trigger will reject the change and throw and error stating such. You can find this in lines 71-100 of mysql_tables.py. <br>
* The next trigger is prevent_same_faculty_insert, which made sure that faculty 1 and faculty 2 were not the same. We did this to make sure the table wasn't populated with self-paths. If a user enters a path with the same faculty member being the start and end faculty, the trigger rejects the change and throws an error. Find this in lines 101-118 of mysql_tables.py.<br>
* And also we created 2 triggers for The Favorite Keyword Widget(add_keyword_trigger_{user_id}, delete_keyword_trigger_{user_id}) to perform database operation on user_favkeyword table. Here we are updating our table(user_favkeyword) when keywords are added or deleted to the temporary table for each user using their IP address. Find this under function create_temp_table() from line no 93-175 of app.py.
  
***Transactions:***
* We used transactions in the collaborator_path table. Whenever a user wants to find a path between 2 different faculty members, the table would update with the 2 faculty member id's as well as the path between them (the path is defined in the below paragraph). This is in lines 169-229 of graph_creator.py. We stored this information so that the user could see the paths between themselves and various faculy members. The path is defined as such: "The path column represents the path of relationships between the two faculty members.
   Each element of this path list is a tuple, containing three parts.
 The first part is the from part, the second is the to part, and the third is the relation part. 
The from and to parts are attributes including faculty members (f), publications (p), keywords (k), 
and institutes (i), and the relation part represents the node that connects the from and to part. "<br>
* The "add_keyword_trigger_{user_id}" trigger fires after an insertion into "user_{user_id}" table. It checks if the inserted keyword exists in another table "user_favkeyword".
If the keyword does not exist, it inserts it into "user_favkeyword" with a count of 1; otherwise, it updates the count. Check 
The "delete_keyword_trigger_{user_id}" trigger fires after a deletion from "user_{user_id}" table. It updates the count of the corresponding keyword in "user_favkeyword" after the deletion. Find this under function create_temp_table() from line no 93-175 of app.py.
Overall this sets up a relational database structure where tables and triggers are created to manage keyword entries and counts based on user interactions. It ensures data integrity and performs necessary actions based on database states and user actions.


**Extra-Credit Capabilities**: 
* The Favorite Keyword Widget(keyword add/delete widget) has useful and cool implementation which involves user-entered keywords, trending search graph, unique user tables, and data cleanup. It creates a unique temporary table for each user using their unique ip address and store their keywords. It implements triggers(add and delete) and transactions to update the user_favkeyword table when keywords are added or deleted. Triggers ensure that certain actions (like updating keyword counts, adding or deleting keywords) occur automatically when data changes. By adding these features, we could actually track the most searched keywords from each user, plot the user treding keyword graph, manage user keywords well, and keep the data clean and the database fast. <br>
* Another extra credit capability we added was the Find Your Match Widget. This is a non-straightforward yet useful functionality extending beyond the scope of the basic applications. We used all 3 of the databases for this. For MySQL, we created a view of university names which allowed us to create the university dropdown menu, we created an index on the name attribute for keywords which allowed us to check the existence of a keyword faster, and we created the collaborator path_table with triggers and constraints which allowed us to store various paths between different faculty members. For Neo4j, we used the shortest path algorithm to create a map between two faculty members, which relied on the existing relationships (AFFILIATED_WITH, PUBLISH, INTERESTED_IN, and LABEL_BY) to connect the bridge between these two faculty members. For MongoDB, we used the university name chosen from the drop down menu and the keyword name inputted by the user to filter out and display the relavent faculty members with keyword and university. This can be pretty useful for a faculty member who wants to learn about other researchers in a particular field, and can learn how he/she connects with those researchers. 


**Contributions**: How each member has contributed, in terms of 1) tasks done and 2) time spent?<br>

| Team Member | UIUC ID | Widgets | Hours Spent |
| --- | --- | --- | --- |
| Saswati Munshi | saswati2 | Planing and designing, Faculty search,  Search Top 10 Faculty for Keyword, Favorite Keywords Dashboard | 30 hours |
| Caleb Satvedi | csatve2 | Planing and designing, Data for Publications by Year for Keyword, Data for Publications by Year for University, Find Your Match | 30 hours  |
