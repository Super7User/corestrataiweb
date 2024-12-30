import json
from flask import Flask,Blueprint, request, jsonify, render_template


shapes_blueprint = Blueprint('shapes_blueprint', __name__)

FILE_PATH = "D:/shapes.json"

# Endpoint to save shapes
@shapes_blueprint.route('/save_shapes', methods=['POST'])
def save_shapes():
    try:
        shapes = request.json.get('shapes', [])
        with open(FILE_PATH, 'w') as file:
            json.dump(shapes, file)
        return jsonify({"message": "Shapes saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to load shapes
@shapes_blueprint.route('/load_shapes', methods=['GET'])
def load_shapes():
    try:
        with open(FILE_PATH, 'r') as file:
            shapes = json.load(file)
        return jsonify(shapes), 200
    except FileNotFoundError:
        return jsonify([]), 200  # Return empty list if no shapes file exists
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to render the canvas page
@shapes_blueprint.route('/videodownloadsample')
def videodownloadsample():
    return render_template('videodownloadsample.html')

# if __name__ == '__main__':
#     shapes_blueprint.run(debug=True)
