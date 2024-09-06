from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file, Response
from flask_login import login_required, current_user
from dotenv import load_dotenv, find_dotenv
from groq import Groq
import pandas as pd
import ast
import time
from firebase_admin import credentials, auth, db
import logging

tools_blueprint = Blueprint('tools', __name__)

load_dotenv(find_dotenv())
# client = OpenAI(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")
client = Groq(api_key='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')


@tools_blueprint.route('/tools')
@login_required
def tools():
    category = request.args.get('category', None)
    search_query = request.args.get('search', None)
    data = pd.read_csv('alltools.csv')

    user_id = session.get('userId')
    print(user_id, "userId")

    if category and category != "All":
        data = data[data['Category'] == category]

    if search_query:
        data = data[data['PromptSystem'].str.contains(search_query, case=False, na=False)]

    tools_data = data.to_dict(orient='records')
    categories = data['Category'].dropna().unique().tolist()

    session['tool_ids'] = data['ID'].tolist()

    user_email = current_user.email if current_user.is_authenticated else None

    return render_template('tools2.html', tools_data=tools_data, categories=categories, user_email=user_email)

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    try:
        response =client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        return f"Error: {e}"

@tools_blueprint.route('/tool-detail/<string:tool_id_str>')
def tool_detail(tool_id_str):
    try:
        tool_id = int(float(tool_id_str))
        session['tool_id'] = tool_id
    except ValueError:
        return "Invalid Tool ID", 400   

    data = pd.read_csv('alltools.csv')
    tool_details = data.to_dict(orient='records')

    tool = next((item for item in tool_details if item['ID'] == tool_id), None)
    if tool is None:
        return "Tool not found", 404

    tool['Fields'] = ast.literal_eval(tool['Fields']) if pd.notna(tool['Fields']) else []
    font_family = tool.get('Font')
    titleName = tool.get('Title')
    print(font_family, "tool")
    print(titleName, "titleName")
    
    return render_template('tool_details.html', tool=tool, tool_id=tool_id, fontDynamic=font_family, titleName=titleName)

@tools_blueprint.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.get_json()
    prompt = data['prompt']
    response_message = "I am available"
    return jsonify(message=response_message)

@tools_blueprint.route('/generate-stream', methods=['POST'])
def generate_stream():
    data = request.get_json()
    prompt = data.get('prompt')
    user_id = session.get('userId')

    if not prompt:
        return jsonify({'error': 'Prompt is missing'}), 400

    tool_id = session.get('tool_id')

    try:
        df = pd.read_csv('alltools.csv')
        tool_details = df[df['ID'] == int(tool_id)]
        if tool_details.empty:
            return jsonify({'error': 'Tool not found'}), 404

        system_prompt = tool_details.iloc[0]['PromptSystem']
        tool_title = tool_details.iloc[0]['Title']
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            stream=True,
            temperature=1,
            max_tokens=512,
            top_p=1,
        )

        complete_response = ""

        def generate():
            nonlocal complete_response
            content_generated = False

            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    complete_response += content
                    yield content
                    content_generated = True
                else:
                    print("No content in chunk or malformed chunk:", chunk)

            if content_generated:
                ref = db.reference('generated_streams').push()
                ref.set({
                    'user_id': user_id,
                    'tool_id': tool_id,
                    'tool_title': tool_title,
                    'prompt': prompt,
                    'response': complete_response,
                    'timestamp': int(time.time() * 1000)
                })

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        print("Error during streaming:", str(e))
        return jsonify({'error': str(e)}), 500

@tools_blueprint.route('/tooldetailoutput/<int:tool_id>', methods=['GET'])
def tool_details_output(tool_id):
    user_id = session.get('userId')

    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 400

    try:
        ref = db.reference('generated_streams')
        query = ref.order_by_child('user_id').equal_to(user_id)
        result = query.get()

        last_entry = None
        for key, value in result.items():
            if value['tool_id'] == tool_id:
                last_entry = value
                break

        if not last_entry:
            return jsonify({'error': 'Data not found for this tool'}), 404

        last_entry['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_entry['timestamp'] / 1000))

        return render_template('tooldetail_Ouput.html', data=last_entry)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_blueprint.route('/get_info', methods=['POST'])
def get_info():
    product_name = request.form['product_name']
    prompt = f"Tell me about {product_name}"
    response = get_completion(prompt)
    return response

