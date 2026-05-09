from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from flasgger import Swagger
import os
from datetime import datetime
from flask_cors import CORS
import pandas as pd 
load_dotenv()

app = Flask(__name__)

# ---------------- SWAGGER INIT ----------------
swagger = Swagger(app)

# ---------------- MONGO ----------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

expenses = db["expenses"]
logs = db["logs"]

# ---------------- HOME ----------------
@app.route("/", methods=["GET"])
def home():
    """
    Home Route
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "Smart Expense Tracker API Running 🚀"})

# ---------------- ADD EXPENSE ----------------
@app.route("/expenses", methods=["POST"])
def add_expense():
    """
    Add Expense
    ---
    parameters:
      - in: body
        name: body
        required: true
    responses:
      201:
        description: Expense added
    """
    data = request.json
    result = expenses.insert_one(data)

    return jsonify({
        "message": "Expense added",
        "id": str(result.inserted_id)
    }), 201

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    """
    Upload CSV File
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      200:
        description: CSV uploaded successfully
    """
    try:
        file = request.files["file"]

        df = pd.read_csv(file)
        records = df.to_dict(orient="records")

        if records:
            expenses.insert_many(records)

        return jsonify({
            "message": "CSV uploaded successfully",
            "records": len(records)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- GET EXPENSES ----------------
@app.route("/expenses", methods=["GET"])
def get_expenses():
    """
    Get All Expenses
    ---
    responses:
      200:
        description: List of expenses
    """
    data = list(expenses.find({}, {"_id": 0}))
    return jsonify(data)

# ---------------- UPDATE EXPENSE ----------------
@app.route("/expenses/<title>", methods=["PUT"])
def update_expense(title):
    """
    Update Expense
    ---
    responses:
      200:
        description: Expense updated
    """
    data = request.json
    expenses.update_one({"title": title}, {"$set": data})

    return jsonify({"message": "Updated successfully"})

# ---------------- DELETE EXPENSE ----------------
@app.route("/expenses/<title>", methods=["DELETE"])
def delete_expense(title):
    """
    Delete Expense
    ---
    responses:
      200:
        description: Expense deleted
    """
    expenses.delete_one({"title": title})
    return jsonify({"message": "Deleted successfully"})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)