from flask import Flask
app = Flask(__name__)

@app.route('/')
def run_script():
    #return 'Hello, World!'

    data = request.get_json()

    name = data.get("name")
    age = data.get("age")

    result = process_inputs(name, age)

    return jsonify({"result": result})
