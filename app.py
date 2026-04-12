from flask import Flask, request, jsonify, render_template
import csv

app = Flask(__name__)

# ---- the actual fuckin logic for reading the material data and doing a brute force algorithm ----
def process_inputs(start, target, highest):
    materials = []
    material_names = []

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
                material_names.append(row[0])
                
                numeric_row = []
                for cell in row[1:]:
                    try:
                        numeric_row.append(int(cell))
                    except ValueError:
                        numeric_row.append(0)
                if numeric_row:
                    materials.append(numeric_row)
    
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

    materials_required = [
        {"name": name, "count": int(count)}
        for name, count in zip(material_names, best_solution)
        if count > 0
    ]
        
    return {
        "start": start,
        "target": target,
        "materials": materials_required,
        "material_names": material_names,
        "total": best_count
    }

def validate(start, target):
    if len(start) != len(target):
        raise ValueError("Stat lists must be the same length")

    for i, (a, b) in enumerate(zip(start, target)):
        if b < a:
            raise ValueError("target stats must not be lower than current limits")

# ---- Homepage ----
@app.route("/")
def home():
    return render_template(
        "mainPage.html",
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
        return render_template(
            "mainPage.html",
            error=str(e),
            start=raw_start,
            target=raw_target,
            highest=raw_highest
        )

    result = process_inputs(raw_start, raw_target, raw_highest)

    return render_template(
        "resultsPage.html",
        start = result["start"],
        target = result["target"],
        total = result["total"],
        materials = result["materials"],
        material_list = result["material_names"]
    )
