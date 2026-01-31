import streamlit as st
import pandas as pd
from backend import process_query

st.set_page_config(page_title="NL to SQL", layout="wide")

st.title("Natural Language to SQL (PostgreSQL)")

st.markdown(
    "Ask a question in plain English. The system will generate **safe SQL** and execute it."
)

# User input
question = st.text_input("Enter your question")

if st.button("Run Query"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL and executing query..."):
            result = process_query(question)

        if "error" in result:
            st.error(result["error"])
        elif "generation_error" in result:
            st.error(result["generation_error"])
        else:
            st.subheader("Generated SQL")
            st.code(result["sql"], language="sql")
            df = pd.DataFrame(result["rows"], columns=result["columns"])
            st.subheader("Query Results")
            st.dataframe(df)
