from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file, Response
from flask_login import login_required, current_user
from dotenv import load_dotenv, find_dotenv
from groq import Groq
import pandas as pd
import ast
import time
from firebase_admin import credentials, auth, db,firestore
import logging
import redis
import holygrailutils


tools_blueprint = Blueprint('tools', __name__)


load_dotenv(find_dotenv())
# client = OpenAI(api_key="sk-proj-jJllTB6aYWrrwO7DLLm9T3BlbkFJO7PocWpToNQ1rD77LXWf")
clientg = Groq(api_key='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')
redis_client = redis.Redis(host='localhost', port=6379, db=0)
# redis_client = holygrailutils.get_redis_client()


@tools_blueprint.route('/tools')
@login_required
def tools():
    user_id = current_user.get_id()

    if user_id:

        redis_user_id = redis_client.hget(user_id, "user_id")
        redis_email = redis_client.hget(user_id, "email")

        redis_user_id = redis_user_id.decode('utf-8') if redis_user_id else None
        redis_email = redis_email.decode('utf-8') if redis_email else None

        if redis_user_id and user_id == redis_user_id:
            db = firestore.client()
            user_doc = db.collection('users').document(user_id).get()
            
            
            user_data = user_doc.to_dict()
            firestore_plan = user_data.get('plan')  
            if not firestore_plan:
                return jsonify({"status": "error", "message": "Plan not found for user in Firestore"}), 404
            print(f"Plan from Firestore: {firestore_plan}")
        else:
            return jsonify({"status": "error", "message": "User ID mismatch"}), 403
    else:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    category = request.args.get('category', None)
    search_query = request.args.get('search', None)
    data = pd.read_csv('alltools.csv')

    if category and category != "All":
        data = data[data['Category'] == category]

    if search_query:
        data = data[data['PromptSystem'].str.contains(search_query, case=False, na=False)]

    tools_data = data.to_dict(orient='records')
    categories = data['Category'].dropna().unique().tolist()
    session['currentPlan'] = firestore_plan
    print(firestore_plan, "Fetched plan...")

   
    return render_template(
        'tools2.html',
        tools_data=tools_data,
        categories=categories,
        user_email=redis_email,
        plan=firestore_plan
    )


def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}]
    try:
        response =clientg.chat.completions.create(
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
        user_id = current_user.get_id()

        if user_id:
            redis_user_id = redis_client.hget(user_id, "user_id")
            redis_email = redis_client.hget(user_id, "email")
            redis_plan = redis_client.hget(user_id, "plan")
            
            
            if redis_user_id:
                redis_user_id = redis_user_id.decode('utf-8')
            if redis_email:
                redis_email = redis_email.decode('utf-8')
            if redis_plan:
                redis_plan = redis_plan.decode('utf-8')
            
            
            if user_id == redis_user_id:
                print(f"User ID: {redis_user_id}, Email: {redis_email}, Plan: {redis_plan}")
            else:
                return jsonify({"status": "error", "message": "User ID mismatch"}), 403
        else:
            return jsonify({"status": "error", "message": "User not logged in"}), 401

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

    return render_template(
        'tool_details.html',
        tool=tool,
        tool_id=tool_id,
        fontDynamic=font_family,
        titleName=titleName,
        plan=redis_plan
    )

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
    # user_id = session.get('userId')
    # user_plan = session.get('plan')
    unique_id = session.get('firebase_unique_id')
    user_id = current_user.get_id()

    if user_id:
            redis_user_id = redis_client.hget(user_id, "user_id")
            redis_email = redis_client.hget(user_id, "email")
            redis_plan = redis_client.hget(user_id, "plan")
            
            
            if redis_user_id:
                redis_user_id = redis_user_id.decode('utf-8')
            if redis_email:
                redis_email = redis_email.decode('utf-8')
            if redis_plan:
                redis_plan = redis_plan.decode('utf-8')
            
            
            if user_id == redis_user_id:
                print(f"User ID: {redis_user_id}, Email: {redis_email}, Plan: {redis_plan}")
            else:
                return jsonify({"status": "error", "message": "User ID mismatch"}), 403
    else:
            return jsonify({"status": "error", "message": "User not logged in"}), 401


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
        response = clientg.chat.completions.create(
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
                # ref = db.reference('generated_streams').push()
                ref = db.reference(f'generated_streams/{unique_id}')
                ref.update({
                    'user_id': user_id,
                    'tool_id': tool_id,
                    'tool_title': tool_title,
                    'prompt': prompt,
                    'response': complete_response,
                    # 'plan':user_plan,
                    'timestamp': int(time.time() * 1000)
                })

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        print("Error during streaming:", str(e))
        return jsonify({'error': str(e)}), 500

@tools_blueprint.route('/tooldetailoutput/<int:tool_id>', methods=['GET'])
def tool_details_output(tool_id):
    user_id = session.get('userId')
    user_id = current_user.get_id()

    if user_id:
        redis_user_id = redis_client.hget(user_id, "user_id")
        redis_email = redis_client.hget(user_id, "email")
        redis_plan = redis_client.hget(user_id, "plan")
        
        if redis_user_id:
            redis_user_id = redis_user_id.decode('utf-8')
        if redis_email:
            redis_email = redis_email.decode('utf-8')
        if redis_plan:
            redis_plan = redis_plan.decode('utf-8')
        
        if user_id == redis_user_id:
            print(f"User ID: {redis_user_id}, Email: {redis_email}, Plan: {redis_plan}")
        else:
            return jsonify({"status": "error", "message": "User ID mismatch"}), 403
    else:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

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

        return render_template('tooldetail_Ouput.html', data=last_entry, plan=redis_plan)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_blueprint.route('/get_info', methods=['POST'])
def get_info():
    product_name = request.form['product_name']
    prompt = f"Tell me about {product_name}"
    response = get_completion(prompt)
    return response


