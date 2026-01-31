import faiss
import numpy as np
from openai import OpenAI

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

client=OpenAI(api_key='your_api_key')
embeddings = []
for text in schema_knowledge_base:
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embeddings.append(res.data[0].embedding)

embeddings = np.array(embeddings).astype("float32")

# create faiss index
index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(embeddings)

#save index
faiss.write_index(index, "schema.index")
