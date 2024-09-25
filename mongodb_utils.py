'''
Database access: You will write a few python functions organized in a 
few files like mysql_utils.py, mongodb_utils.py, and neo4j_utils.py to 
access the databases using their query languages via their network interfaces to support the widgets. 
'''
from pymongo import MongoClient

'''
to run: python mongodb_utils.py
'''


def connect_to_mongodb():
    # Connect to MongoDB server
    try:
        # Connect to MongoDB (adjust the URI as necessary)
        client = MongoClient('localhost', 27017)
        print("Connected to MongoDB")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    # client = MongoClient('localhost', 27017)

    # # Access the 'academicworld' database
    # db = client['academicworld']

    # # List collections
    # collections = db.list_collection_names()

    # if collections:
    #     print("Collections in 'academicworld' database:")
    #     for collection in collections:
    #         print(collection)
    # else:
    #     print("No collections found in 'academicworld' database.")
    # return client

# def main():
#     # Connect to MongoDB server
#     client = MongoClient('localhost', 27017)

#     # Access the 'academicworld' database
#     db = client['academicworld']

#     # List collections
#     collections = db.list_collection_names()

#     if collections:
#         print("Collections in 'academicworld' database:")
#         for collection in collections:
#             print(collection)
#     else:
#         print("No collections found in 'academicworld' database.")


if __name__ == "__main__":
    connect_to_mongodb()
