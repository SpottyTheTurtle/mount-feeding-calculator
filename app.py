from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ---- Your logic ----
def process_inputs(start, goal):
    return {
        "start": start,
        "goal": goal,
    }

def validate(start, goal):
    if len(start) != len(goal):
        raise ValueError("Stat lists must be the same length")

    for i, (a, b) in enumerate(zip(start, goal)):
        if b > a:
            raise ValueError("Goal stats must not be lower than current limits")

# ---- HTML page ----
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Test App</title>
</head>
<body>
    <h2>Mount Feeding Calculator</h2>

    <form method="POST" action="/run-form">
        <h3>Enter your mount's current limits</h3>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Speed"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Acceleration"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Altitude"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Energy"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Handling"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Toughness"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Boost"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Training"><br><br>

        <h3>Enter your mount's target limits</h3>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Speed"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Acceleration"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Altitude"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Energy"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Handling"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Toughness"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Boost"><br><br>
        <input name="goal[]" type="number" min="1" step="1" required placeholder="Training"><br><br>

        <h3>Enter your highest trained stat. This will determine what level of food to use in the calculation</h3>
        <input name="highest" type="number" min="1" step="1" required  placeholder="Enter a number"><br><br>

        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""


# ---- Homepage ----
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


# ---- Form handler ----
@app.route("/run-form", methods=["POST"])
def run_form():
    try:
        start = request.form.getlist("start[]")
        goal = request.form.getlist("goal[]")
        highest = request.form.get("highest")

        validate(start, goal)

    except ValueError as e:
        return f"<h3>Error: {str(e)}</h3><br><a href='/'>Go back</a>"

    result = process_inputs(start, goal)

    return f"""
    <h3>Result:</h3>
    <p>Set A: {result['start']}</p>
    <p>Set B: {result['goal']}</p>
    <br><a href='/'>Go back</a>
    """


# ---- JSON API ----
@app.route("/run", methods=["POST"])
def run_api():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    start = data.get("start", [])
    goal = data.get("goal", [])

    result = process_inputs(start, goal)

    return jsonify(result)


# ---- Local run ----
if __name__ == "__main__":
    app.run(debug=True)
