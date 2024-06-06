# Mongo-2-Dynamo

Migrating a database from MongoDB was not a good experience using AWS DMS so I wrote this script to move my data instead, the script also saves .xlsx sheets of the data locally as a restore point incase something happens during migration , so that you don't need to re-query the entire db again.
The script also supports sending messages to a team channel to keep you up to date with the progress of the migration without being on the machine it's running on.  

## Prerequisites

The script has the following external libraries: 

boto3: ```pip install boto3``` 
pymongo: ```pip install pymongo[srv]```
pymsteams: ```pip install pymsteams```
pandas: ```pip install pandas```

## How to use 

Install the libraries , and from there replace the constants in the DynamoUpload.py script to your database info or to reference your ENV variable. From there's it's as simple as pressing run and waiting a couple hrs for the entire db to be moved. 

### PRO TIP‼️:This script can run locally but , for your own sanity it's probably best to run it on an EC2 machine or a machine with reliable connectivity as any major network disruptions will stop the migration mid way.
### WARNING⚠️: Works for all the datatypes that were in my database but if you're using something that can raise an error in dynamo , you should convert the field before upload. Like what I did in the migrate_collection method line 57 for float to Decimal


