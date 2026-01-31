# text-to-sql-project

<h4>Setup instructions</h4>

1.create database in postgresSQL

2.create table using the schema.sql files

3.feed the data using insert_data.sql

4.insert openai apikey in the backend.py

5.run streamlit app and use natural language to sql convertor.

<h4>Accuracy & Hallucination Reduction</h4>
To reduce halluciantions we used rules based check system.
Used searching method to search DROP,DELETE,TRUNCATE,UPDATE,INSERT in generated sql query
All used similar method to check column name and table name are correct or not.
If wrong query is generated then the sql query is not generated.
