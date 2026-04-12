from flask import Flask, request, jsonify, render_template_string
import csv

app = Flask(__name__)

# this essentially tells the code where to put each of the different material bonuses. could've hardcoded it into the csv or filled the blank spaces with 0s in code but like, idfk, if it works it works.
mask = [
    [0,0,0,1,0,1,0,0],
    [1,0,0,1,0,0,0,1],
    [1,1,0,0,0,1,0,0],
    [0,0,1,0,0,0,1,0],
    [0,1,0,0,1,0,1,0],
    [1,0,1,0,0,0,0,0],
    [0,0,1,0,1,0,0,1],
    [0,1,0,1,0,0,0,0]
]

# ---- Your logic ----
def process_inputs(start, target, highest):
    data = []
    with open('materials.csv', newline='') as csvfile:
        csvr = list(csv.reader(csvfile))
        index = None
        
        for i, row in enumerate(csvr):
            if row[0].isdigit():
                num = int(row[0])
                if num <= highest:
                    index = i
                else:
                    break

        if index is not None:
            for row in csvr[index + 1 : index + 1 + 8]:
                numeric_row = []
                for cell in row:
                    try:
                        numeric_row.append(int(cell))
                    except ValueError:
                        continue
                if numeric_row:
                    data.append(numeric_row)

    # map the materials from whichever level resource you're using to the right places for the brute force algorithm
    materials = []
    for mask_row, data_row in zip(mask, data):
        result = []
        val_index = 0
        for m in mask_row:
            if m == 1:
                result.append(data_row[val_index])
                val_index += 1
            else:
                result.append(0)
        materials.append(result)

    
    best_solution = None
    best_count = float('inf')

    def backtrack(stats, counts, index=0):
        nonlocal best_solution, best_count, target

        # Prune branches if they're worst than the current best
        if sum(counts) >= best_count:
            return

        # Did we do it?
        if all(s >= t for s, t in zip(stats, target)):
            best_solution = counts[:]
            best_count = sum(counts)
            return

        if index >= len(materials):
            return

        # Calculate max quantity for each material (to limit the brute force algorithm and ensure it finishes sometime in the next century)
        max_qty = 0
        for s, t, m in zip(stats, target, materials[index]):
            if m > 0:
                needed = (t - s + m - 1) // m
                max_qty = max(max_qty, needed)

        # Try all quantities from 0 up to max_qty
        for qty in range(max_qty + 1):
            new_stats = [s + qty*m for s, m in zip(stats, materials[index])]
            counts[index] = qty
            backtrack(new_stats, counts, index + 1)
            counts[index] = 0

    backtrack(start[:], [0]*len(materials)) # hopefully this remains 8. if it is not 8, then gods help you.

    material_names = ["ingot", "gem", "plank", "paper", "string", "grains", "oil", "meat"]
    materials_required = [
        {"name": name, "count": count}
        for name, count in zip(material_names, best_solution)
        if count > 0
    ]
        
    return {
        "start": start,
        "target": target,
        "materials": materials_required,
        "total": best_count
    }

def validate(start, target):
    if len(start) != len(target):
        raise ValueError("Stat lists must be the same length")

    for i, (a, b) in enumerate(zip(start, target)):
        print(a)
        print(b)
        if b < a:
            raise ValueError("target stats must not be lower than current limits")

# ---- HTML page ----
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Test App</title>
</head>
<body>
    <h2>Mount Feeding Calculator</h2>

    {% if error %}
        <p style="color:red;"><strong>{{ error }}</strong></p>
    {% endif %}

    <form method="POST" action="/run-form">
        <h3>Enter your mount's current limits</h3>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Speed"
            value="{{ start[0] if start|length > 0 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Acceleration"
               value="{{ start[1] if start|length > 1 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Altitude"
               value="{{ start[2] if start|length > 2 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Energy"
               value="{{ start[3] if start|length > 3 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Handling"
               value="{{ start[4] if start|length > 4 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Toughness"
               value="{{ start[5] if start|length > 5 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Boost"
               value="{{ start[6] if start|length > 6 else '' }}"><br><br>
        <input name="start[]" type="number" min="10" step="1" required placeholder="Training"
               value="{{ start[7] if start|length > 7 else '' }}"><br><br>

        <h3>Enter your mount's target limits</h3>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Speed"
            value="{{ target[0] if target|length > 0 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Acceleration"
               value="{{ target[1] if target|length > 1 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Altitude"
               value="{{ target[2] if target|length > 2 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Energy"
               value="{{ target[3] if target|length > 3 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Handling"
               value="{{ target[4] if target|length > 4 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Toughness"
               value="{{ target[5] if target|length > 5 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Boost"
               value="{{ target[6] if target|length > 6 else '' }}"><br><br>
        <input name="target[]" type="number" min="1" step="1" required placeholder="Training"
               value="{{ target[7] if target|length > 7 else '' }}"><br><br>

        <h3>Enter your highest trained stat. This will determine what level of food to use in the calculation</h3>
        <input name="highest" type="number" min="1" step="1" required
            placeholder="Enter a number"
            value="{{ highest or '' }}"><br><br>

        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

RESULT_PAGE = """
<h2>Result</h2>
<p>Start: {{ start }}</p>
<p>target: {{ target }}</p>

<h3>Materials required: {{ total }}</h3>
<ul>
    {% for item in materials %}
        <li>{{ item.count }} {{ item.name }}</li>
    {% endfor %}
</ul>

<br><a href="/">Go back</a>
"""


# ---- Homepage ----
@app.route("/")
def home():
    return render_template_string(
        HTML_PAGE,
        start=[],
        target=[],
        highest=""
    )


# ---- Form handler ----
@app.route("/run-form", methods=["POST"])
def run_form():
    try:
        raw_start = list(map(int, request.form.getlist("start[]")))
        raw_target = list(map(int, request.form.getlist("target[]")))
        raw_highest = int(request.form.get("highest"))

        validate(raw_start, raw_target)
        
    except ValueError as e:
        return render_template_string(
            HTML_PAGE,
            error=str(e),
            start=raw_start,
            target=raw_target,
            highest=raw_highest
        )

    result = process_inputs(raw_start, raw_target, raw_highest)

    return render_template_string(
        RESULT_PAGE,
        start = result["start"],
        target = result["target"],
        total = result["total"],
        materials = result["materials"]
    )
#    <p>Highest: {result['highest']}</p>

# ---- JSON API ----
@app.route("/run", methods=["POST"])
def run_api():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    start = data.get("start", [])
    target = data.get("target", [])

    result = process_inputs(start, raw_target)

    return jsonify(result)


# ---- Local run ----
if __name__ == "__main__":
    app.run(debug=True)
