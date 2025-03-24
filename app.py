import streamlit as st
import pandas as pd
import phpserialize
from io import BytesIO

# Function to check if a string looks like serialized PHP data
def is_serialized(s):
    return isinstance(s, str) and s.startswith('a:') and s.endswith(';}')

# Function to decode byte strings
def decode_bytes(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')
    return s

# Function to decode byte strings in JSON data
def decode_json_bytes(json_data):
    decoded_data = {}
    for key, value in json_data.items():
        if isinstance(value, bytes):
            decoded_data[key] = value.decode('utf-8')
        else:
            decoded_data[key] = value
    return decoded_data

# Function to deserialize PHP-serialized data
def deserialize_php(serialized_data):
    try:
        deserialized = phpserialize.loads(bytes(serialized_data, 'utf-8'))
        return decode_json_bytes(deserialized)
    except:
        return {}

# Function to format column names
def format_column_name(name):
    if isinstance(name, str):
        name = name.replace('-', ' ').replace('_', ' ').title()
    return name

# Function to clean column names
def clean_column_names(df):
    df.columns = [decode_bytes(col) for col in df.columns]
    df.columns = [format_column_name(col) for col in df.columns]

# Streamlit UI
st.set_page_config(page_title="PHP Serialized Data Processor", layout="wide")
st.title("PHP Serialized Data Processor")
st.write("Upload a CSV file with PHP serialized data, and this app will process and clean it.")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    clean_column_names(df)
    
    for column in df.columns:
        df[column] = df[column].apply(decode_bytes)
    
    processed_df = df.copy()
    
    for column in df.columns:
        if df[column].apply(is_serialized).all():
            st.write(f"Processing column: {column}")
            deserialized_data = df[column].apply(deserialize_php)
            json_df = pd.json_normalize(deserialized_data)
            clean_column_names(json_df)
            processed_df = processed_df.drop(columns=[column])
            processed_df = pd.concat([processed_df, json_df], axis=1)
    
    st.success("Data processing complete! You can download the cleaned CSV file below.")
    
    # Convert DataFrame to CSV for download
    output = BytesIO()
    processed_df.to_csv(output, index=False)
    output.seek(0)
    st.download_button("Download Processed CSV", output, file_name="processed_data.csv", mime="text/csv")
