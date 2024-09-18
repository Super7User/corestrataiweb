import pandas as pd
from flask import Flask, render_template, request, session
from flask_login import login_required, current_user


app = Flask(__name__)

@app.route('/header')
@login_required
def header():
    # Fetch the category and search query parameters from the request
    category = request.args.get('category', None)
    search_query = request.args.get('search', None)

    # Read the tools data from CSV (alltools.csv)
    tools_data_df = pd.read_csv('alltools.csv')

    # Fetch the user ID from the session
    user_id = session.get('userId')
    print(user_id, "userId")

    # Filter data by category if provided and not "All"
    if category and category != "All":
        tools_data_df = tools_data_df[tools_data_df['Category'] == category]

    # Filter data by search query if provided
    if search_query:
        tools_data_df = tools_data_df[tools_data_df['PromptSystem'].str.contains(search_query, case=False, na=False)]

    # Convert tools data to dictionary format
    tools_data = tools_data_df.to_dict(orient='records')
    categories = tools_data_df['Category'].dropna().unique().tolist()

    # Save tool IDs in session for future use
    session['tool_ids'] = tools_data_df['ID'].tolist()

    # Fetch user profile details from demotools.csv based on user_id
    users_df = pd.read_csv('demotools.csv')

    # Assuming user_id corresponds to email (Mail_id column in the CSV)
    user_profile = users_df[users_df['Mail_id'] == user_id].to_dict(orient='records')

    if not user_profile:
        user_profile = None  # In case user profile is not found

    # Current user email (for profile or other purposes)
    user_email = current_user.email if current_user.is_authenticated else None

    return render_template(
        'tools2.html', 
        tools_data=tools_data, 
        categories=categories, 
        user_email=user_email, 
        user_profile=user_profile  # Pass profile data to the template
    )
