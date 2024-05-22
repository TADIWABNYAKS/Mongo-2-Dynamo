'''
Script to migrate data from mongoDB collections to an AWS DynamoDB table 
'''
import json
import time
from decimal import Decimal
import boto3
import pandas as pd
import pymsteams
from pymongo import MongoClient

# Configuration Constants (Fill in with your details or use environment/ENV variables)
DYNAMODB_REGION = ''
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
DYNAMODB_TABLE_NAME = ''
TEAMS_WEBHOOK_URL = ''
MONGO_CONNECTION_STRING = ''
MONGO_DB_NAME = ''

#Initalize database connections ;
dynamodb = boto3.resource(
    'dynamodb',
    region_name=DYNAMODB_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)
teams_message = pymsteams.connectorcard(TEAMS_WEBHOOK_URL)
client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]

def query_mongo(collection_name):
    """Query all documents from a MongoDB collection."""
    collection = db[collection_name]
    return collection.find({})

def save_to_excel(df_list, sheet_list, file_name):
    """Save multiple DataFrames locally to an Excel file with specified sheet names."""
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for df, sheet in zip(df_list, sheet_list):
            df.to_excel(writer, sheet_name=sheet, startrow=0, startcol=0, index=False)

def migrate_collection(collection):
    """Migrate data from a MongoDB collection to DynamoDB and save to a local DataFrame."""
    cursor = query_mongo(collection)
    mongo_docs = list(cursor)
    df = pd.DataFrame(mongo_docs)
    
    # Convert DataFrame to JSON for DynamoDB
    json_data = df.to_json(orient="records", index=True)
    parsed_data = json.loads(json_data, parse_float=Decimal)  # DynamoDB requires Decimal for float values
    
    # Insert documents into DynamoDB
    for doc in parsed_data:
        table.put_item(Item=doc)
        print(doc)
    
    # Limit sheet name length for Excel
    sheet = collection
    if len(collection) > 30:
        sheet = collection[:30] 
    return df, sheet

def send_teams_message(message):
    """Send a message to Microsoft Teams."""
    teams_message.text(message)
    teams_message.send()

if __name__ == '__main__':
    df_list = []
    sheet_list = []
    
    try:
        send_teams_message(f"Migration for {MONGO_DB_NAME} started")
        
        for collection_name in db.list_collection_names():
            df, sheet_name = migrate_collection(collection_name)
            df_list.append(df)
            sheet_list.append(sheet_name)
            
            send_teams_message(f"Migration for {collection_name} finished")
            time.sleep(5)  # Avoid hitting rate limits or overwhelming the destination
        
        save_to_excel(df_list, sheet_list, f"{MONGO_DB_NAME}_migration.xlsx")
        
        send_teams_message("Migration complete")
    except Exception as e:
        error = str(e)
        print(error)
        send_teams_message(f"Error during migration: {error}")
        send_teams_message(f"Error on collection: {collection_name}")
    
    
