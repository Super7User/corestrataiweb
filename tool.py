from flask import Flask, request, session, render_template
from flask_login import login_required, current_user
import pandas as pd

app = Flask(__name__)

@app.route('/tools')
@login_required
def tools():
    category = request.args.get('category', None)
    search_query = request.args.get('search', None)
    data = pd.read_csv('alltools.csv')

    user_id = session.get('userId')
    print(user_id,"userId")

    if category and category != "All":
        data = data[data['Category'] == category]

    if search_query:
        data = data[data['PromptSystem'].str.contains(search_query, case=False, na=False)]

    tools_data = data.to_dict(orient='records')
    categories = data['Category'].dropna().unique().tolist()
 
    session['tool_ids'] = data['ID'].tolist()

    user_email = current_user.email if current_user.is_authenticated else None
  
    return render_template('tools2.html', tools_data=tools_data, categories=categories, user_email=user_email)

if __name__ == '__main__':
    app.run(debug=True)
