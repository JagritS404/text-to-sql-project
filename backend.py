import faiss
import numpy as np
from openai import OpenAI
import re
import psycopg2
client =OpenAI(api_key='your_api_key')
index = faiss.read_index("schema.index")


schema_knowledge_base=[
    "Table: customers - stores customer information",
    "Column: customers.id | primary key of customers",
    "Column: customers.name | customer full name",
    "Column: customers.phone | customer phone number",
    "Column: customers.city | city where customer lives",
    "Table: products - stores products information",
    "Column: products.id | primary key of products",
    "Column: products.name | product name",
    "Column: products.category | product category",
    "Column: products.price | product price",
    "Table: orders - stores order information",
    "Column: orders.id | primary key of orders",
    "Column: orders.customer_id | foreign key referencing customers.id",
    "Column: orders.order_date | date when order was placed",
    "Column: orders.status | status of orders (placed,shipped,delivered,cancelled)",
    "Table: order_items - stores individual items from each order",
    "Column: order_items.id | primary key of order_items",
    "Column: order_items.order_id | foreign key referencing orders.id",
    "Column: order_items.product_id | foreign key referencing products.id",
    "Column: order_items.quantity | quantity of each product",
    "Column: order_items.unit_price | price of product at time of order",
    "Join: orders.customer_id = customers.id",
    "Join: order_items.order_id = orders.id",
    "Join: order_items.product_id = products.id"
]

def give_prompt(user_question,useful_schema_context):
    return f"""

        You are an expert PostgresSql generator.
        Rules:
        -Give ONLY SQL no explanation 
        -Use ONLY the  tables and columns provide in schema
        -Use ONLY SELECT queries
        -DO NOT  use INSERT,DELETE,DROP,ALTER,UPDATE,TRUNCATE queries
        -Always qualify every column using table_name.column_name.
        -Do NOT use table aliases.
        -Use explict join whenever it is possible
        -If question can not be answer using schema and rules, say:CANNOT_ANSWER.

        Schema:{useful_schema_context}
        Question:{ user_question}
        Generate SQL."""


def retrieve_schema(query: str, k: int = 5):
    """
    Returns top-k relevant schema text chunks for a user query
    """
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    query_vector = np.array([embedding]).astype("float32")
    _, indices = index.search(query_vector, k)

    return [schema_knowledge_base[i] for i in indices[0]]

def check_invalid_keywords(sql_query):
    sql_upper=sql_query.upper()
    list=["INSERT","DELETE","DROP","ALTER","UPDATE","TRUNCATE"]

    for x in list:
        if x in sql_upper:
            return False
    return True

valid_tables=["customers","products","orders","order_items"]
valid_columns = {
    "customers": {"id", "name", "phone", "city"},
    "products": {"id", "name", "category", "price"},
    "orders": {"id", "customer_id", "order_date", "status"},
    "order_items": {"id", "order_id", "product_id", "quantity", "unit_price"},
}

def check_table(sql_query):
    sql_lower=sql_query.lower()
    tables=re.findall( r"(?:from|join)\s+([a-z_]+)",sql_lower)

    for x in tables:
        if x not in valid_tables:
            return False
    return True


def check_columns(sql_query):
    sql_lower = sql_query.lower()
    all_columns = re.findall(r"([a-z_]+)\.([a-z_]+)",sql_lower)

    for t, c in all_columns:
        if t not in valid_tables:
            return False
        if c not in valid_columns[t]:
            return False
    return True



def generate_sql(user_question):
    useful_schema_context=retrieve_schema(user_question)
    prompt=give_prompt(user_question,useful_schema_context)
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )
    sql = response.output_text.strip()
    return sql


    
def process_query(question):
    sql_query=generate_sql(question)
    if(sql_query=='CANNOT_ANSWER'):
        return {"generation_error":"Can't answer this question using avaliable schema or question contains invalid operations"}
    elif(not check_invalid_keywords(sql_query) or not  check_table(sql_query) or not  check_columns(sql_query)):
        return {"generation_error":"Invalid query generated.Please rephrase message"}
    else:
        try:
            connection = psycopg2.connect(
            dbname="dbname",
            user="user_name",
            password="password",
            host="localhost"
            )
            cursor=connection.cursor()
            cursor.execute(sql_query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return {
                "sql": sql_query,
                "columns": columns,
                "rows": rows
            }
        except Exception as e:
            return {
                "error": f"Database error: {str(e)}"
            }






