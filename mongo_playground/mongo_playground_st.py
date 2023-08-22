import streamlit as st
from dotenv import load_dotenv
import re
import os
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

_ = load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

def get_explanation(response):
    prefix_string = "Explanation:"
    start_index = response.find(prefix_string)
    if start_index != -1:
        start_index += len(prefix_string)
        end_index = response.find("\n\n", start_index)
        if end_index == -1:
            end_index = len(response)
        extracted_text = response[start_index:end_index].strip()
        return extracted_text
    return ""

def get_aggregation_pipeline(response):
    pattern = r'```javascript(.*?)```'
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Sorry, we couldn't generate the query for this input! Please try again later."

def construct_response(aggregation_pipeline, explanation):
    print(f"Aggregation Pipeline: {aggregation_pipeline}")
    print(f"Explanation: {explanation}")
    return {
        "aggregation_pipeline": aggregation_pipeline,
        "explanation": explanation
    }

def generate_query_using_openai(input_data, output_data, model="gpt-3.5-turbo"):

    print("Generate query using OpenAI directly")

    prompt = f"""
    Your task is to write a MongoDB query  
    to produce the output similar to "Sample output data" 
    for the input data provided in "Sample input data". 

    Please check the query that you write produces exact output 
    that matches the "Sample output data".

    Please provide the response in a JSON format so that 
    each part of the response can be easily parsed. 
    
    Please ensure to do the following in the response.
    1. Place the MongoDB queries in the response within these two texts
    opening tag - ```javascript, end tag - ```. Only the query needs to 
    be present between those two tags and don't provide any other text. 
    2. Provide the explanation of the query after the query. 
    Prefix the explanation of the query with "Explanation: " string. 
     
    The sample input and sample output data is given below.
    Sample input data: ```{input_data}```
    Sample output data: ```{output_data}```
    """

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0
    )

    print(f"Response from ChatGPT: {response}")

    aggregation_pipeline = get_aggregation_pipeline(response.choices[0].message["content"])
    explanation = get_explanation(response.choices[0].message["content"])
    
    # Parse the response to extract aggregati# Parse the response to extract aggregation pipeline and explanation separately
    return construct_response(aggregation_pipeline, explanation)

def generate_query_using_langchain(input_data, output_data, model="gpt-3.5-turbo"):

    print("Generate query using Langchain")

    prompt_template_string = """
    Your task is to write a MongoDB query  
    to produce the output similar to "Sample output data" 
    for the input data provided in "Sample input data". 

    Please check the query that you write produces exact output 
    that matches the "Sample output data".

    Please provide the response in a JSON format so that 
    each part of the response can be easily parsed. 
    
    Please ensure to do the following in the response.
    1. Place the MongoDB queries in the response within these two texts
    opening tag - ```javascript, end tag - ```. Only the query needs to 
    be present between those two tags and don't provide any other text. 
    2. Provide the explanation of the query after the query. 
    Prefix the explanation of the query with "Explanation: " string. 

    The sample input and sample output data is given below.
    Sample input data: ```{input_data}```
    Sample output data: ```{output_data}```
    """
    # Instantiate the model
    chat = ChatOpenAI(temperature=0.0)
    
    # Create the prompt template from the string
    prompt_template = ChatPromptTemplate.from_template(prompt_template_string)

    print(f"Prompt: {prompt_template.messages[0].prompt}")
    print(f"Prompt: {prompt_template.messages[0].prompt.input_variables}")

    user_messages = prompt_template.format_messages(
                                        input_data=input_data,
                                        output_data=output_data
                                    )
    
    print(f"User Message: {user_messages[0]}")

    # Invoke the LLM to get the generate query
    response = chat(user_messages)

    print(f"Response from LLM: {response.content}")

    aggregation_pipeline = get_aggregation_pipeline(response.content)
    explanation = get_explanation(response.content)

    # Extract just the aggregation pipeline
    return construct_response(aggregation_pipeline, explanation)

def generate_query():
    llm_backend = st.session_state.llm_backend
    input_data = st.session_state.input_data
    output_data = st.session_state.output_data

    if llm_backend == "OpenAI":
        response = generate_query_using_openai(input_data, output_data)
    else:
        response = generate_query_using_langchain(input_data, output_data)

    st.session_state.generated_query = response["aggregation_pipeline"]
    st.session_state.explanation = response["explanation"]

def initialize_state():
    if 'generated_query' not in st.session_state:
        st.session_state.generated_query = ""

    if 'explanation' not in st.session_state:
        st.session_state.explanation = ""

def setup_ui():
    st.set_page_config(layout="wide")

    st.header("MongoDB Query Generator")
    st.write("This tool generates the MongoDB query \
             for a given data input and an expected data output. \
             It works well for simple to medium complexity use cases.")
    
    with st.form("query_form"):

        row_0 = st.columns(3)
        row_0[0].selectbox("**LLM backend**", ['OpenAI', "Langchain"], key="llm_backend")

        row_1 = st.columns(3)
        row_1[0].text_area("**Input Data**", label_visibility="visible", key="input_data", height=400)
        row_1[1].text_area("**Output Data**", label_visibility="visible", key="output_data", height=400) 
        row_1[2].text_area("**Generated Query**", label_visibility="visible", key="generated_query", height=400)

        st.text_area("**Explanation**", key="explanation")

        st.form_submit_button("Generate Query", on_click=generate_query)

    initialize_state()

def main():
    setup_ui()

if __name__ == "__main__":
    main()