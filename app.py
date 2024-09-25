'''
Dashboard specification: You will write a python file app.py, 
which uses Dash (and other libraries like Pandas, and Numpy) 
to declaratively create widgets and their layout.
'''


import graph_creator
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import mysql_utils1
from dash import dash_table
from dash_table import DataTable
import mongodb_utils
import pandas as pd
import plotly.express as px
from dash_html_components import Img
from datetime import datetime
import mysql
#import time
#from contextlib import closing
from flask import request
import mysql_tables
from dash.exceptions import PreventUpdate


# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

connection = mysql_utils1.connect_to_mysql()
cursor = connection.cursor()

mysql_tables.tables()

valid_names = False

textbox_content = """
In the above table, there are 3 columns: Faculty1 ID, Faculty2 ID and Path.
 The first two represent your's and the other faculty member's id repsectively. 
 The path column represents the path of relationships between the two faculty members.
   Each element of this path list is a tuple, containing three parts.
 The first part is the from part, the second is the to part, and the third is the relation part. 
The from and to parts are attributes including faculty members (f), publications (p), keywords (k), 
and institutes (i), and the relation part represents the node that connects the from and to part. 
"""


def get_ip_address():
    # If running as a web application
    if request:
        return request.remote_addr
    else:
        # Using socket library to fetch IP address
        import socket
        return socket.gethostbyname(socket.gethostname())

# Function to generate a new session ID (replace with your logic)


def generate_session_id():
    session_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return session_id  # Example session ID


# Get or generate the session ID
user_id = get_ip_address()
user_id = user_id.replace(".", "_")
print(user_id)

try:
    cursor.execute("SHOW TABLES LIKE 'user_favkeyword'")
    table_exists = cursor.fetchone()

    # If user_favkeyword table does not exist, create it
    if not table_exists:
        create_table_query = """
        CREATE TABLE user_favkeyword (
            keyword VARCHAR(512) PRIMARY KEY,
            keyword_count INT DEFAULT 0  
        )
        """
        cursor.execute(create_table_query)

        ### add some basic data ###

        insert_table_query = """INSERT INTO user_favkeyword (keyword, keyword_count) VALUES ('machine learning', 13), ('data mining', 15), ('computer graphics', 23), ('cloud computing', 10), ('network security', 8);"""

        cursor.execute(insert_table_query)
        connection.commit()
        print("user_favkeyword table created and inserted some values...")
except:
    pass


def create_temp_table():
    try:
        search_query = f"SHOW TABLES LIKE 'user_{user_id}'"
        cursor.execute(search_query)
        table_exists = cursor.fetchone()

        if not table_exists:
            create_table_query = f"""
            CREATE TABLE user_{user_id} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                keyword VARCHAR(255)
            );
            """
            cursor.execute(create_table_query)
        else:
            print("user_id table already exists...")

    except mysql.connector.Error as err:
        # If an error occurs, print the error message
        print(f"Error creating table: {err}")

    # Check if user table table exists

    search_query = f"SHOW TABLES LIKE 'user_{user_id}'"
    cursor.execute(search_query)
    table_exists = cursor.fetchone()

    if table_exists:
        # Check if add_keyword_trigger already exists
        cursor.execute(f"SHOW TRIGGERS LIKE 'add_keyword_trigger_{user_id}'")
        add_trigger_exists = cursor.fetchone()

        # Create add_keyword_trigger if it doesn't exist
        if not add_trigger_exists or len(add_trigger_exists) == 0:

            cursor.execute(
                f"DROP TRIGGER IF EXISTS add_keyword_trigger_{user_id}")

            cursor.execute(f"""
            CREATE TRIGGER add_keyword_trigger_{user_id} AFTER INSERT ON user_{user_id}
            FOR EACH ROW
            BEGIN
                DECLARE keyword_exists INT;
                
                -- Check if the keyword already exists in user_favkeyword
                SELECT COUNT(*) INTO keyword_exists FROM user_favkeyword WHERE keyword = NEW.keyword;
                
                -- If the keyword does not exist, insert it with count 1; otherwise, update count
                IF keyword_exists = 0 THEN
                    INSERT INTO user_favkeyword (keyword, keyword_count) VALUES (NEW.keyword, 1);
                ELSE
                    UPDATE user_favkeyword SET keyword_count = keyword_count + 1 WHERE keyword = NEW.keyword;
                END IF;
            END;
            """)
            print(f"add_keyword_trigger_{user_id} created.")
        # Check if delete_keyword_trigger already exists
        cursor.execute(
            f"SHOW TRIGGERS LIKE 'delete_keyword_trigger_{user_id}'")
        delete_trigger_exists = cursor.fetchone()

        # Create delete_keyword_trigger if it doesn't exist
        if not delete_trigger_exists:
            cursor.execute(
                f"DROP TRIGGER IF EXISTS delete_keyword_trigger_{user_id}")

            cursor.execute(f"""
            CREATE TRIGGER delete_keyword_trigger_{user_id} AFTER DELETE ON user_{user_id}
            FOR EACH ROW
            BEGIN
                UPDATE user_favkeyword SET keyword_count = keyword_count - 1 WHERE keyword = OLD.keyword;
            END;
            """)
            print(f"delete_keyword_trigger_{user_id} created.")

        if add_trigger_exists and delete_trigger_exists:
            print("Triggers already exist.")

        print("Triggers checked and created/confirmed.")
    else:
        print(f"user_{user_id} table does not exist.")


create_temp_table()
cool_font = {'fontFamily': 'Arial, sans-serif', 'color': 'darkblue'}
cool_colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'header': '#007bff',
}
widget_style = {
    'margin': '20px 0',
}


app.layout = html.Div([

    html.Div(
        children=[
            html.H1("Faculty Collaboration Network",
                    style={'margin-bottom': '0'}),
            html.P("Collaborate, Create, Inspire",
                   style={'margin-top': '0'}),
        ],
        style={'textAlign': 'center', 'padding': '20px',
               'backgroundColor': '#333', 'color': 'white'}
    ),


    html.H1("Faculty search:", style={'color': 'darkblue'}),
    html.Div([
        dcc.Input(id='faculty-input', type='text',
                  placeholder='Enter faculty name'),
        html.Button('Search', id='search-button_facultysearch',
                    n_clicks=0, style={'margin': '10px'})
    ], style={'marginBottom': '10px'}),

    html.Div(id='table-container'),

    html.H1("Data for Publications by Year for Keyword",
            style={'color': 'darkblue'}),

    html.Div([
        dcc.Input(id='input-keyword', type='text',
                  placeholder='Enter a keyword...'),
        html.Button('Submit', id='submit-button1',
                    n_clicks=0,  style={'margin': '10px'})
    ]),

    dcc.Graph(id='publications-graph'),



    dcc.Interval(
        id='interval-component1',
        interval=60 * 1000,  # Interval set to 1 minute
        n_intervals=0
    ),


    html.H1("Search Top 10 Faculty for Keyword:", style={'color': 'darkblue'}),
    html.Div([
        dcc.Input(id='keyword-input', type='text',
                  placeholder='Enter a keyword...', style={'margin': '10px'}),
        html.Button('Search', id='search-button_krc',
                    n_clicks=0, style={'margin': '10px'})
    ], style={'marginBottom': '10px'}),

    html.Div(id='search-results'),



    html.Div([
        html.Div([
            html.H1("Favorite Keywords Dashboard",
                    style={'color': 'darkblue'}),
            dcc.Input(id='fab_keyword-input', type='text',
                      placeholder='Enter a keyword...', style={'margin': '10px'}),
            html.Button('Add Keyword', id='add-keyword-btn',
                        n_clicks=0, style={'margin': '10px'}),
            dcc.Input(id='delete-keyword-input', type='text',
                      placeholder='Enter a keyword to delete...', style={'margin': '10px'}),
            html.Button('Delete Keyword', id='delete-keyword-btn',
                        n_clicks=0, style={'margin': '10px'}),
            html.Div(id='keyword-list'),
            html.Div(id='output-container-button'),
            html.Div(id='recommendations-container'),
            html.Button('Clear Search', id='clear-search-button'),
        ], style={'width': '50%', 'float': 'left'}),


        html.Div([
            html.H1("Keyword Trend Graph",  style={'color': 'darkblue'}),
            dcc.Graph(id='keyword-trend-graph', figure={}),
        ], style={'width': '50%', 'float': 'right'}),
    ], style={'width': '100%', 'display': 'flex'}),


    html.H1("Data for Publications by Year for University",
            style={'color': 'darkblue'}),

    html.Div([
        dcc.Input(id='input-university', type='text',
                  placeholder='Enter a University Name...'),
        html.Button('Submit', id='submit-button2',
                    n_clicks=0, style={'margin': '10px'}),
    ]),

    dcc.Graph(id='publications-graph-uni'),


    dcc.Interval(
        id='interval-component2',
        interval=60 * 1000,  # Interval set to 1 minute
        n_intervals=0
    ),

    dcc.Interval(
        id='interval-component3',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0
    ),

    html.H1("Find Your Match: ",
            style={'color': 'darkblue'}),
    dcc.Dropdown(
        id='uni-dropdown',
        options=[],
        multi=False,
        placeholder='Select university...',
        searchable=True,  # Allow filtering by typing
        style={'width': '50%'}  # Set the width to 100% to match the layout
    ),
    dcc.Input(id='my-input', value='', type='text',
              placeholder='Type keyword...'),
    html.Button('Submit', id='uni_key_button',
                n_clicks=0, style={'margin': '10px'}),
    html.Div(id='output-container', style={'fontSize': 18}),
    html.Label('Enter your name:', style={
               'color': 'blue', 'fontWeight': 'bold', }),
    dcc.Input(id='name-input', value='', type='text',
              placeholder='Enter your name...', style={'margin': '10px'}),
    html.Label('Enter faculty name:', style={
               'color': 'blue', 'fontWeight': 'bold', }),
    dcc.Input(id='faculty-input1', value='', type='text',
              placeholder='Enter faculty name...', style={'margin': '10px'}),
    html.Button('Submit', id='faculty_button',
                n_clicks=0, style={'margin': '10px'}),
    html.Div(id='output-container2', style={'fontSize': 18}),
    html.Div(
        children=[
            html.H3("Faculty Path Table", style={'color': 'darkblue'}),
            dcc.Interval(
                id='interval-component4',
                interval=5000,  # Update every 5 seconds
                n_intervals=0
            ),
            html.Div(id='live-update-table')
        ]
    ),
    html.Div([
        dcc.Textarea(
            id='my-textarea',          # Unique identifier for this input
            value=textbox_content,  # Content to display in the text box
            readOnly=True,          # Make the text box read-only
            # CSS style to set width to 50%
            style={'width': '50%', 'height': '150px'}
        )
    ])


])


@ app.callback(Output('live-update-table', 'children'),
               [Input('interval-component1', 'n_intervals')])
def update_table(n):

    df = None

    # Connect to MySQL and fetch data
    connection = mysql_utils1.connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM collaborator_path")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    df.rename(columns={'faculty1_id': 'Faculty1 ID',
              'faculty2_id': 'Faculty2 ID', 'Path': 'Path'}, inplace=True)

    # Create the HTML table
    table_header = [html.Th(col, style={
                            'backgroundColor': cool_colors['header'], 'color': 'white'}) for col in df.columns]
    table_body = [html.Tr([html.Td(df.iloc[i][col], style={
        'fontFamily': 'Quicksand',
        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        'whiteSpace': 'normal',
        'textAlign': 'left',
        'backgroundColor': cool_colors['background'],
        'color': cool_colors['text'],
    }) for col in df.columns]) for i in range(len(df))]
    table = html.Table([html.Thead(html.Tr(table_header)),
                       html.Tbody(table_body)], className='table')

    # Apply CSS styling
    table_style = {'overflowX': 'auto'}

    # Wrap the table in a div for additional styling if needed
    return html.Div(table, style=table_style)


@ app.callback(
    [Output('uni-dropdown', 'options'),
     Output('output-container', 'children')],
    [Input('uni-dropdown', 'search_value'),
     Input('uni-dropdown', 'value'),
     Input('uni_key_button', 'n_clicks')],
    [State('my-input', 'value')]
)
def collaborator_idea_uni(search_value, selected_value, n_clicks, keyword):
    ctx = dash.callback_context
    triggered_component = ctx.triggered[0]['prop_id'].split('.')[0]

    connection = mysql_utils1.connect_to_mysql()
    if connection:
        cursor = connection.cursor()
        if triggered_component == 'uni-dropdown':
            if search_value:
                cursor.execute(
                    "SELECT * FROM university_names WHERE name LIKE %s;", ("%" + search_value + "%",))
            else:
                cursor.execute("SELECT * FROM university_names;")
            result = cursor.fetchall()
            options = [{'label': name, 'value': name} for (name,) in result]
            return options, f'Searched name: {search_value}' if search_value else ''
        elif triggered_component == 'uni_key_button' and n_clicks > 0:
            if selected_value and keyword:
                idx_key_query = "SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = 'academicworld'   AND table_name = 'keyword'   AND index_name = 'idx_key_name';"
                cursor.execute(idx_key_query)
                r = cursor.fetchall()
                if r is not None and r[0][0] > 0:
                    print("The idx_name view exists.")
                else:
                    cursor.execute(
                        "CREATE INDEX idx_key_name ON keyword (name);")
                key_query = "SELECT COUNT(name) FROM keyword WHERE name = %s"
                cursor.execute(key_query, (keyword,))
                result = cursor.fetchall()
                if result is not None and result[0][0] == 0:
                    return [], f'Inputted keyword: {keyword} does not exist'
                else:
                    names = graph_creator.findProfs(selected_value, keyword)
                    if names == None:
                        return [], f'Selected University: {selected_value}, Inputted keyword: {keyword}, No Available Faculty'
                    else:
                        return [], f'Selected University: {selected_value}, Inputted keyword: {keyword}, Available Faculty: {names}'
            else:
                return [], ''
        raise PreventUpdate
    else:
        return [], 'Connection to MySQL failed'


@ app.callback(
    Output('output-container2', 'children'),
    [Input('faculty_button', 'n_clicks')],
    [State('name-input', 'value'),
     State('faculty-input1', 'value')]
)
def display_names(n_clicks, name, faculty_name):
    if n_clicks > 0:
        if name and faculty_name:
            # Process the names and display them
            connection = mysql_utils1.connect_to_mysql()
            if connection:
                cursor = connection.cursor()
                query = "SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = 'academicworld'   AND table_name = 'faculty'   AND index_name = 'idx_name';"
                cursor.execute(query)
                r = cursor.fetchall()
                if r is not None and r[0][0] > 0:
                    print("The idx_name view exists.")
                else:
                    cursor.execute("CREATE INDEX idx_name ON faculty (name);")

                name_checker = "SELECT COUNT(name) from FACULTY where name = %s;"
                cursor.execute(name_checker, (name,))
                r = cursor.fetchall()
                if r is not None and r[0][0] == 0:
                    return f"The name {name} does not exist"

                cursor.execute(name_checker, (faculty_name,))
                r = cursor.fetchall()
                if r is not None and r[0][0] == 0:
                    return f"The name {faculty_name} does not exist"
            df = graph_creator.collaborator(name, faculty_name)
            print(df)
            # relationship_text = ""
            # for index, row in df.iterrows():
            #     print(row['rel_type'])
            rel_text = graph_creator.rel_explainer(df)
            print(rel_text)
            return f'Your name: "{name}" \t  Faculty name: "{faculty_name}" \n {rel_text}'
        else:
            return 'Please enter both your name and faculty name.'
    else:
        return ''


@app.callback(
    Output('publications-graph', 'figure'),
    [Input('submit-button1', 'n_clicks'),
     Input('interval-component2', 'n_intervals')],
    [State('input-keyword', 'value')]
)
def pub_keyword(submit_n_clicks, interval_n, keyword):
    if submit_n_clicks:
        df = graph_creator.helper(keyword)
    else:
        df = graph_creator.helper("machine learning")

    fig = px.line(df, x='year', y='num_publications',
                  title=f'Number of Publications Over Years: {keyword}')

    fig.update_traces(line=dict(color=fig_style_keyword['line_color'], dash=fig_style_keyword['line_dash']),
                      marker=dict(symbol=fig_style_keyword['marker']))
    return fig


@app.callback(
    Output('publications-graph-uni', 'figure'),
    [Input('submit-button2', 'n_clicks'),
     Input('interval-component3', 'n_intervals')],
    [State('input-university', 'value')]
)
def pub_uni(submit_n_clicks, interval_n, university):
    if submit_n_clicks:
        df = graph_creator.helper2(university)
    else:
        df = graph_creator.helper2("Elon University")

    fig = px.line(df, x='year', y='num_publications',
                  title=f'Number of Publications Over Years: {university}')

    fig.update_traces(line=dict(color=fig_style_university['line_color'], dash=fig_style_university['line_dash']),
                      marker=dict(symbol=fig_style_university['marker']))
    return fig


# CSS style for image cells
IMAGE_CELL_STYLE = {
    'maxWidth': '50px',
    'maxHeight': '50px',
    'overflow': 'hidden',
    'backgroundSize': 'cover',
}


fig_style_keyword = {
    'line_color': 'blue',
    'line_width': 3.5,  # Thicker line
    'line_dash': 'solid',
    'marker': 'circle'
}

fig_style_university = {
    'line_color': '#17A2B8',  # Teal color
    'line_width': 3.5,  # Thicker line
    'line_dash': 'dashdot',  # Dash-dot line style
    'marker': 'hexagon',  # Hexagon marker symbol
    'marker_color': '#FF5733',  # Orange marker color
    'marker_size': 10  # Larger marker size
}

recommendations_container_style = {
    'border': '1px solid #007bff',
    'borderRadius': '5px',
    'padding': '5px',
    'margin': '20px 0',
    'backgroundColor': '#e5f2ff',  # Light blue background color
    'color': '#004085',  # Dark blue text color
    'maxWidth': '50%',
}


# Callback to filter data based on search input and update the table

@app.callback(
    Output('table-container', 'children'),
    [Input('search-button_facultysearch', 'n_clicks')],
    [State('faculty-input', 'value')]
)
def search_faculty(n_clicks, faculty_name):
    if n_clicks and faculty_name:
        client = mongodb_utils.connect_to_mongodb()
        # MongoDB query to retrieve faculty details
        if client:
            db = client['academicworld']
            faculty_collection = db['faculty']
            query = {"name": {"$regex": faculty_name, "$options": "i"}}
            faculty_results = faculty_collection.aggregate([
                {"$match": query},
                {
                    "$project": {
                        "id": 1,
                        "name": 1,
                        "position": 1,
                        "researchInterest": 1,
                        "email": 1,
                        "phone": 1,
                        "university_name": "$affiliation.name",
                        "photo_url": "$photoUrl",
                        "_id": 0
                    }
                }, {"$limit": 10}
            ])

            # Convert MongoDB cursor to a list of dictionaries
            faculty_list = list(faculty_results)

        if faculty_list:
            if len(faculty_list) == 1:
                faculty = faculty_list[0]
                return html.Div([
                    html.H3("Faculty Details", style={'color': 'darkblue'}),
                    html.Table([
                        html.Tr([html.Th("", style={'text-align': 'right', 'color': 'darkblue'}), html.Td(
                            html.Img(src=faculty.get('photo_url', ''), style={'width': '250px', 'height': '250px'}))]),
                        html.Tr([html.Th("ID:", style={
                                'text-align': 'right', 'color': 'darkblue'},), html.Td(faculty.get('id', ''))]),
                        html.Tr([html.Th("Name:", style={
                                'text-align': 'right', 'color': 'darkblue'}), html.Td(faculty.get('name', ''))]),

                        html.Tr([html.Th("Position:", style={
                                'text-align': 'right', 'color': 'darkblue'}), html.Td(faculty.get('position', ''))]),
                        html.Tr([html.Th("Research Interest:", style={
                                'text-align': 'right', 'color': 'darkblue'}), html.Td(faculty.get('researchInterest', ''))]),
                        html.Tr([html.Th("Email:", style={
                                'text-align': 'right', 'color': 'darkblue'}), html.Td(faculty.get('email', ''))]),
                        html.Tr([html.Th("Phone:", style={
                                'text-align': 'right', 'color': 'darkblue'}), html.Td(faculty.get('phone', ''))]),
                        html.Tr([html.Th("University Name:", style={
                                'text-align': 'right', 'color': 'darkblue'}), html.Td(faculty.get('university_name', ''))]),
                    ], style={'width': '100%'})
                ])

            else:
                columns = [
                    {'name': 'ID', 'id': 'id'},
                    {'name': 'Name', 'id': 'name'},
                    {'name': 'Position', 'id': 'position'},
                    {'name': 'Research Interest', 'id': 'researchInterest'},
                    {'name': 'Email', 'id': 'email'},
                    {'name': 'Phone', 'id': 'phone'},
                    {'name': 'University Name', 'id': 'university_name'},
                ]

                data_rows = []
                for faculty in faculty_list:
                    row_dict = {
                        'id': faculty.get('id', ''),
                        'name': faculty.get('name', ''),
                        'position': faculty.get('position', ''),
                        'research_interest': faculty.get('researchInterest', ''),
                        'email': faculty.get('email', ''),
                        'phone': faculty.get('phone', ''),
                        'university_name': faculty.get('university_name', ''),
                    }
                    data_rows.append(row_dict)

                return dash_table.DataTable(
                    id='faculty-table',
                    columns=columns,
                    data=data_rows,
                    style_table={'overflowX': 'auto'},
                    style_header={
                        'backgroundColor': cool_colors['header'], 'color': 'white'},
                    style_cell={
                        'fontFamily': 'Quicksand',
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'whiteSpace': 'normal',
                        'textAlign': 'left',
                        'backgroundColor': cool_colors['background'],
                        'color': cool_colors['text'],
                    }
                )

        else:
            return "No data found for the specified faculty."
    else:
        return "Enter a faculty name and click 'Search'."


# calculate krc for entererd keyword and display details using mysql

@app.callback(
    Output('search-results', 'children'),
    [Input('search-button_krc', 'n_clicks')],
    [dash.dependencies.State('keyword-input', 'value')]
)
def krc_mysql(n_clicks, keyword):
    if n_clicks is not None and n_clicks > 0 and keyword:
        #connection = mysql_utils1.connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            query = (" SELECT f.name AS faculty_name, f.position AS position, u.name AS university_name, p.title AS publication_title, "
                     " SUM(pk.score * p.num_citations) AS KRC FROM faculty f JOIN faculty_publication fp ON f.id = fp.faculty_id "
                     " JOIN publication p ON fp.publication_id = p.id JOIN university u ON f.university_id = u.id "
                     " JOIN publication_keyword pk ON p.id = pk.publication_id JOIN keyword k ON pk.keyword_id = k.id "
                     " WHERE k.name = %s GROUP BY  p.title, f.name, f.position, u.name ORDER BY KRC DESC LIMIT 10;")

            cursor.execute(query, (keyword,))
            data = cursor.fetchall()

            if data:
                columns = [  # {'name': 'id', 'id': 'id'},

                    {'name': 'Faculty Name', 'id': 'faculty_name'},
                    {'name': 'Position', 'id': 'position'},
                    {'name': 'University Name', 'id': 'university_name'},
                    {'name': 'Publication Title', 'id': 'publication_title'},
                    {'name': 'KRC VALUE', 'id': 'KRC'}
                ]

                data_rows = []
                for row in data:
                    row_dict = dict(
                        zip(['faculty_name', 'position', 'university_name', 'publication_title', 'KRC'], row))

                    data_rows.append(row_dict)

                return DataTable(
                    id='krc_table',
                    columns=columns,
                    data=data_rows,
                    style_table={'overflowX': 'auto'},
                    style_header={
                        'backgroundColor': cool_colors['header'], 'color': 'white'},
                    # Allow wrapping text in cells
                    #style_data={'whiteSpace': 'normal'},
                    # Adjust cell styles as needed
                    style_cell={
                        'fontFamily': 'Quicksand',
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'whiteSpace': 'normal',
                        'textAlign': 'left',
                        'backgroundColor': cool_colors['background'],
                        'color': cool_colors['text'],
                    }
                )
            else:
                return "No data found for the specified keyword."
        else:
            return "Failed to connect to MySQL."
    else:
        return "Enter a faculty name and click 'Search'."


def cleanup_temporary_tables():

    cursor = connection.cursor()

    drop_table_query = f"DROP TABLE IF EXISTS user_{user_id};"

    cursor.execute(drop_table_query)
    cursor.execute(f"DROP TRIGGER IF EXISTS add_keyword_trigger_{user_id}")
    cursor.execute(f"DROP TRIGGER IF EXISTS delete_keyword_trigger_{user_id}")

    connection.commit()
    print(f"Temporary table #{user_id} dropped.")
    return ""


# Callback to handle adding keywords and show recommendations
@app.callback(
    [Output('output-container-button', 'children'),
     # Clear the input field
     Output('recommendations-container',
            'children'), Output('fab_keyword-input', 'value'),
     Output('delete-keyword-input', 'value'), Output('keyword-trend-graph', 'figure')],
    [Input('add-keyword-btn', 'n_clicks'),
     Input('delete-keyword-btn', 'n_clicks'),
     Input('clear-search-button', 'n_clicks')],
    [State('fab_keyword-input', 'value'),
     State('delete-keyword-input', 'value')]

)
def update_keywords_and_recommendations(add_clicks, delete_clicks, clear_search, new_keyword, delete_keyword):

    if new_keyword or delete_keyword:
        clear_search = None

    create_temp_table()
    if new_keyword:
        new_keyword = new_keyword.lower()
    if delete_keyword:
        delete_keyword = delete_keyword.lower()
    cursor = connection.cursor()
    added_msg = ""

    cursor.execute(f"SELECT keyword FROM user_{user_id}")
    keywords = [row[0] for row in cursor.fetchall()]

    if add_clicks is not None and add_clicks > 0 and new_keyword:
        if new_keyword in keywords:
            print("Enter a different keyword!")
            added_msg = "Enter a different keyword!"
            new_keyword = ''
        else:
            # Add new keyword using trigger
            cursor.execute(
                f"INSERT INTO user_{user_id} (keyword) VALUES (%s)", (new_keyword,))
            connection.commit()
            #keywords_str = ', '.join(keywords)
            #keywords_str = ', '.join(new_keyword)
            keywords_str = ', '.join([str(item) for item in keywords])
            if keywords_str:
                keywords_str = keywords_str + ', '+new_keyword
            else:
                keywords_str = new_keyword
            added_msg = f"Added keywords: {keywords_str}"
            new_keyword = ''

    if delete_clicks is not None and delete_clicks > 0 and delete_keyword:

        if delete_keyword in keywords:
            # Delete keyword using trigger
            cursor.execute(
                f"DELETE FROM user_{user_id} WHERE keyword = %s", (delete_keyword,))
            connection.commit()
            added_msg = f"Deleted keyword: {delete_keyword}"
            delete_keyword = ''

        else:
            added_msg = "Enter a different keyword to delete!"
            delete_keyword = ''
    cursor.execute(f"SELECT keyword FROM user_{user_id}")
    keywords = [row[0] for row in cursor.fetchall()]

    recommendations_html = []
    cursor.execute(
        "SELECT keyword, keyword_count FROM user_favkeyword ORDER BY keyword_count DESC LIMIT 10")

    keyword_data = cursor.fetchall()
    if keyword_data:
        keywords_favkeywords, counts = zip(
            *keyword_data) if keyword_data else ([], [])
        fig = None
        # Create a bar chart using Plotly Express
        fig = px.bar(x=keywords_favkeywords, y=counts, labels={
                     'x': 'Keyword', 'y': 'Count'}, title='Search Keyword Trend')

        # Customize the layout of the graph if needed
        fig.update_layout(xaxis_title='Keywords', yaxis_title='Counts')
    else:
        keywords_favkeywords = None
        fig = None

    if clear_search is not None and clear_search > 0:
        cleanup_temporary_tables()
        clear_search = None
        keywords = []
        return added_msg, html.Div(recommendations_html), new_keyword, delete_keyword, fig
    recommendations = []
    keyword_recommendations = []
    for keyword in keywords:
        # Fetch recommendations based on user_{user_id} table
        query = ("SELECT DISTINCT p.title AS publication_title, f.name AS faculty_name "
                 "FROM faculty f JOIN faculty_publication fp ON f.id = fp.faculty_id "
                 "JOIN publication p ON fp.publication_id = p.id "
                 "JOIN publication_keyword pk ON p.id = pk.publication_id "
                 "JOIN keyword k ON pk.keyword_id = k.id "
                 "JOIN faculty_keyword fk ON f.id = fk.faculty_id "
                 "WHERE k.name = %s "
                 "GROUP BY f.name, p.title "
                 "ORDER BY SUM(pk.score * p.num_citations) DESC LIMIT 3;")

        cursor.execute(query, (keyword,))
        keyword_recommendations = cursor.fetchall()
        print(keyword_recommendations)

        recommendations.append((keyword, keyword_recommendations))
    for keyword, keyword_recommendations in recommendations:
        if len(keyword_recommendations) > 0:
            keyword_html = html.Div([
                html.H3(f"Keyword: {keyword}"),
                html.Ul([html.Li(f"{faculty_name}: {publication_title}") for publication_title,
                        faculty_name in keyword_recommendations], style=recommendations_container_style)
            ])
            recommendations_html.append(keyword_html)
        else:
            keyword_html = html.Div([
                html.H3(f"Keyword: {keyword}"),
                html.Ul([html.Li("No publication found for this keyword")],
                        style=recommendations_container_style)  # Apply style here if needed
            ])
            recommendations_html.append(keyword_html)

    # Check if there is data to display in the graph
    if keywords_favkeywords:
        # Return the graph figure along with other outputs
        return added_msg, html.Div(recommendations_html), new_keyword, delete_keyword, fig
    else:
        # If no data, return None for the graph figure to hide it
        return added_msg, html.Div(recommendations_html), new_keyword, delete_keyword, fig


if __name__ == '__main__':

    app.run_server(debug=True)
    # columns, data_rows = update_table(0)
    # collections = update_table1(0)
