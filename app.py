from flask import Flask, request, jsonify
from flask_cors import CORS
from model import process_financial_data

app = Flask(__name__)
CORS(app)

@app.route('/api/calculate_score', methods=['POST'])
def calculate_score():
    try:
        data = request.json
        print(f"DATA: {data}")
        result = process_financial_data(data.get("transactionData"))
        print(f"result: {result}")
        response = result
        return jsonify(response)
    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
