from flask import Flask, request, render_template, jsonify, Response, flash, redirect, url_for
import pandas as pd
from openai import OpenAI
import time
import ast

app = Flask(__name__)

@app.route('/')
def index_m():
    return render_template('index-m.html')

@app.route('/tools')
def tools():
    category = request.args.get('category', None)
    search_query = request.args.get('search', None)
    data = pd.read_csv('alltools.csv')

    if category:
        data = data[data['Category'] == category]

    if search_query:
        data = data[data['PromptSystem'].str.contains(search_query, case=False, na=False)]

    tools_data = data.to_dict(orient='records')
    categories = data['Category'].dropna().unique().tolist()
    print("It is in tools   1")

    return render_template('tools2.html', tools_data=tools_data, categories=categories)

@app.route('/tool-detail/<string:tool_id_str>')
def tool_detail(tool_id_str):
    # Attempt to convert the tool ID to integer
    try:
        tool_id = int(float(tool_id_str))  # Convert from string to float, then to int
    except ValueError:
        return "Invalid Tool ID", 400  # Return an error for invalid input

    # Read CSV file
    data = pd.read_csv('alltools.csv')
    tool_details = data.to_dict(orient='records')  # Convert data to a list of dictionaries

    # Find the specific tool by ID
    tool = next((item for item in tool_details if item['ID'] == tool_id), None)
    if tool is None:
        return "Tool not found", 404

    # Parse the 'Fields' column
    tool['Fields'] = ast.literal_eval(tool['Fields']) if pd.notna(tool['Fields']) else []

    return render_template('tool_details.html', tool=tool, tool_id=tool_id)



@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.get_json()  # Get JSON data sent from the JavaScript fetch
    prompt = data['prompt']
    
    # Placeholder response, you will later replace this with actual content generation logic
    response_message = "I am available"

    return jsonify(message=response_message)

@app.route('/generate-stream', methods=['POST'])
def generate_stream():

    client = OpenAI(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")
    
    data = request.get_json()  # Get JSON data sent from the JavaScript fetch
    prompt = data['prompt']

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Write a compelling product page copy for my [product/service] that clearly communicates the features and benefits of the product, engages my [target persona], and motivates them to take action."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            stream=True,
            temperature=1,
            max_tokens=256,
            top_p=1,
            )
        print("Response ========", response)
        # Extracting the message from the response
        #messages = response.get('choices', [])[0].get('message.content', {})

        # Function to generate the response stream
        def generate():
            for chunk in response:
                yield chunk.choices[0].delta.content 
        return Response(generate(), mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login1', methods=['POST'])
def log_in():
    username = request.form['username']
    password = request.form['password']
            
    return redirect(url_for('tools'))
    """
    # Here you would validate the credentials, possibly checking against a database
    if username == 'admin' and password == 'admin':  # This is just an example condition
        return redirect(url_for('tools'))
    else:
        flash('Invalid credentials, please try again!')
        return redirect(url_for('login'))  # sRedirect back to the home/login page if credentials are incorrect
    """
@app.route('/contact')
def contect():
    return render_template('contact.html')
   
@app.route('/Home_One')
def index1():
    return render_template('index.html')

@app.route('/Home_Two')
def index2():
    return render_template('index-2.html')

@app.route('/Home_Three')
def index3():
    return render_template('index-3.html')

@app.route('/Home_One_Dark')
def index1dark():
    return render_template('index-dark.html.html')

if __name__ == '__main__':
    app.run(debug=True)


