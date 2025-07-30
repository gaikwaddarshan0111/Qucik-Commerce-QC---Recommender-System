# app.py
from flask import Flask, jsonify, request, render_template # Import render_template
from recommender import QuickCommerceRecommender
import os

app = Flask(__name__)

# Set up paths for templates and static files
app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')
app.static_folder = os.path.join(os.path.dirname(__file__), 'static')

recommender = None
try:
    if not os.path.exists('products.csv') or not os.path.exists('user_interactions.csv'):
        raise FileNotFoundError("products.csv or user_interactions.csv not found. Please run the data simulation script first.")
    recommender = QuickCommerceRecommender()
except FileNotFoundError as e:
    print(f"CRITICAL ERROR: {e}")
    print("Please ensure 'products.csv' and 'user_interactions.csv' are in the same directory.")
except Exception as e:
    print(f"ERROR during recommender initialization: {e}")

@app.route('/')
def home():
    # Render the HTML template for the UI
    return render_template('index.html')

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    if recommender is None:
        return jsonify({"error": "Recommender system not initialized due to previous errors. Check server logs."}), 500

    user_id = request.args.get('user_id', type=int)
    product_id = request.args.get('product_id', type=int)
    num_recs = request.args.get('num_recommendations', default=5, type=int)

    if num_recs <= 0:
        return jsonify({"error": "num_recommendations must be a positive integer."}), 400

    recommendations = recommender.recommend_hybrid(user_id=user_id, product_id=product_id, num_recommendations=num_recs)

    if not recommendations:
        print(f"No recommendations generated for product_id={product_id}, user_id={user_id} after all attempts.")
        return jsonify({"message": "No recommendations available based on current data or context. Try a different request."}), 200

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)