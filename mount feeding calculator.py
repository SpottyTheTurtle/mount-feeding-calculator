import re
import csv

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

def ensure_valid_input(prompt, minimum):
    while True:
        value = input(prompt)
        if value.isdigit():
            value = int(value)
            if value >= minimum:
                return value
        print("invalid value, try again")


stats = ["Speed", "Acceleration", "Altitude/Jump Height", "Energy", "Handling", "Toughness", "Boost", "Training"]

print("Please Enter your mount's current limits")
start = []
for i in range(8):
    stat = ensure_valid_input(f"{stats[i]}: ", 10)
    start.append(stat)

print("\nPlease Enter your mount's target stats (if you don't know exactly, max stats also works)")
target = []
for i in range(8):
    stat = ensure_valid_input(f"{stats[i]}: ", start[i])
    target.append(stat)

print("\nAnd finally, please enter your mount's highest trained stat. This is what determinines the level of the materials being used")
while True:
    highest = ensure_valid_input("highest: ", 1)
    if highest > max(start):
        print("Your highest stat cannot be higher than your limits. Please try again.")
    else:
        print("Thank you! One moment...\n")
        break


#start = [int(x) for x in input("Please enter a comma-separated list of your mount's stats in order. eg: 30,10,20,10,10,10,10,10.\n>").split(',')]
#target = [int(x) for x in input("Please enter the list of your mount's target/max stats, in the same fashion as above.\n>").split(',')]
#highest = int(max(start))

# look. it's fucky, and mildly janky, and pretty horrible, but it does *work*. and that's all that really matters at the end of the day. better than hardcoading each table anyways.
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


# Yippee I love brute force algorithms this definitely won't take 10 years to run
# okay but in all seriousness i tried a greedy search but found it imperfect and when one more ingredient means 6 more hours of waiting i decided,
# given the number of ingredients and relatively low variance in levels, brute force works well enough. if it's too slow i'll rewrite it in C or Rust or something idfk

best_solution = None
best_count = float('inf')

def backtrack(stats, counts, index=0):
    global best_solution, best_count

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

print("Total materials used:", best_count)

# can you tell ilerned what zips were while working on this project?
material_names = ["ingot", "gem", "plank", "paper", "string", "grains", "oil", "meat"]
print("Materials required:")
for name, count in zip(material_names, best_solution):
    if count > 0:
        print(f"{count} {name}")

