from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import re
import json
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#Load OpenAI Key from env file
_ = load_dotenv()
#openai.api_key = os.environ["OPENAI_API_KEY"]
#openai.api_key = "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" #Office
#openai.api_key = "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" #New Key
#openai.api_key = "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"

@app.route("/")
def render_index_page():
    return render_template('index.html')

@app.post("/generate-query")
def generateQuery():
    app.logger.info("Recieved request to generate a query")

    # Get the query parameter from the request
    use_langchain = request.args.get("use_langchain")
    app.logger.info(f"use_langchain: {use_langchain}")

    # Get the request body from the POST request
    data = request.get_json()
    app.logger.info(f"Data: {data}")

    input_data = data.get("inputData")
    output_data = data.get("outputData")

    if use_langchain is not None and use_langchain.lower() == "true":
        aggregation_pipeline = generate_query_using_langchain(input_data, output_data)
    else:
        aggregation_pipeline = generate_query_using_openai(input_data, output_data)

    response = {
        "inputData": input_data,
        "outputData": output_data,
        "generatedQuery": aggregation_pipeline
    }

    return response

# Generate Query by directly talking to OpenAI API
def generate_query_using_openai(input_data, output_data, model="gpt-3.5-turbo"):

    app.logger.info("Generate query using OpenAI directly")

    prompt = f"""
    Your task is to write a MongoDB query  
    to produce the output similar to "Sample output data" 
    for the input data provided in "Sample input data". 

    Please check the query that you write produces exact output 
    that matches the "Sample output data".

    Please provide the response in a JSON format so that 
    each part of the response can be easily parsed.

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

    app.logger.info(f"Response from ChatGPT: {response}")

    # Parse the response to extract aggregati# Parse the response to extract aggregation pipeline and explanation separately
    return get_aggregation_pipeline(response.choices[0].message["content"])

# Generate Query using Langchain
def generate_query_using_langchain(input_data, output_data, model="gpt-3.5-turbo"):

    app.logger.info("Generate query using Langchain")

    prompt_template_string = """
    Your task is to write a MongoDB query  
    to produce the output similar to "Sample output data" 
    for the input data provided in "Sample input data". 

    Please check the query that you write produces exact output 
    that matches the "Sample output data".

    Please provide the response in a JSON format so that 
    each part of the response can be easily parsed.

    The sample input and sample output data is given below.
    Sample input data: ```{input_data}```
    Sample output data: ```{output_data}```
    """
    # Instantiate the model
    chat = ChatOpenAI(temperature=0.0)
    
    # Create the prompt template from the string
    prompt_template = ChatPromptTemplate.from_template(prompt_template_string)

    app.logger.info(f"Prompt: {prompt_template.messages[0].prompt}")
    app.logger.info(f"Prompt: {prompt_template.messages[0].prompt.input_variables}")

    user_messages = prompt_template.format_messages(
                                        input_data=input_data,
                                        output_data=output_data
                                    )
    
    app.logger.info(f"User Message: {user_messages[0]}")

    # Invoke the LLM to get the generate query
    response = chat(user_messages)

    app.logger.info(f"Response from LLM: {response.content}")

    # Extract just the aggregation pipeline
    return get_aggregation_pipeline(response.content)

# Parse the output and extract just the MongoDB pipeline
def get_aggregation_pipeline(response):
    pattern = r'```javascript(.*?)```'
    match = re.search(pattern, response, re.DOTALL)

    if match:
        aggregation_pipeline = match.group(1).strip()
        app.logger.info("Extracted Aggregation Pipeline:")
        app.logger.info(aggregation_pipeline)
    else:
        aggregation_pipeline = "Sorry, we couldn't generate the query for this input! Please try again later."
        app.logger.info("Aggregation pipeline not found in the output")

    return aggregation_pipeline