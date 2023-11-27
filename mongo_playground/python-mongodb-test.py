from pymongo import MongoClient
from dotenv import dotenv_values
from pandas import DataFrame

config = dotenv_values(".env")

doc_1 = {
    "name": "Selvam",
    "age": "37",
    "occupation": "IT",
    "country": "India"
}

doc_2 = {
    "name": "Rupa",
    "age": "37",
    "occupation": "IT",
    "country": "US"
}

doc_3 = {
    "name": "Monu",
    "age": "6",
    "occupation": "Playing",
    "country": "US"
}

doc_4 = {
    "name": "Shriya",
    "age": "6",
    "occupation": "Studying",
    "country": "US"
}

def get_database(config):
    #CONNECTION_STRING = "mongodb+srv://selvam:vnA0WRL9OJqVyzrC@playground.cwfqcov.mongodb.net/?retryWrites=true&w=majority"
    #DB_NAME="pymongo_tutorial"

    client = MongoClient(config["CONNECTION_STRING"])
    return client[config["DB_NAME"]]

def insert_data(collection_name):
    collection_name.insert_many([doc_1, doc_2, doc_3, doc_4])

def get_data(collection_name):
    items = list(collection_name.find())
    for item in items:
        print(item)

    #for item in items:
    #    print(f"Name: {item['name']}, Country: {item['country']}")

    items_df = DataFrame(items)
    print(items_df)

def get_data_using_aggregation(collection_name):
    aggregation_pipeline = [
                    {
                        "$match":
                        {
                            "age": '37',
                        }
                    },
                    {
                        "$project":
                        {
                            "_id": 0,
                            "name": 1,
                            "age": 1,
                            "country": 1,
                        }
                    }
                ]
    items = list(collection_name.aggregate(aggregation_pipeline))
    items_df = DataFrame(items)
    print(items_df)

if __name__ == "__main__":
    db_name = get_database(config)
    collection_name = db_name["test"]
    #insert_data(collection_name)
    get_data(collection_name)
    get_data_using_aggregation(collection_name)

