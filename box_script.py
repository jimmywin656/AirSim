data = """0 0.3078125 0.68046875 0.078125 0.0890625
0 0.55 0.64921875 0.053125 0.0640625
9 0.5171875 0.75859375 0.021875 0.0203125
9 0.41796875 0.621875 0.0296875 0.03125
9 0.3984375 0.74296875 0.015625 0.0171875"""

# Split the input into lines
lines = data.split("\n")

# Iterate over each line, remove the first number, and reformat the remaining values
output = []
for line in lines:
    values = line.split()
    x, y, width, height = map(float, values[1:])  # Skip the first number and convert to float
    output.append(f"({x:.5f}, {y:.5f}, {width:.5f}, {height:.5f})")

# Print the output
for item in output:
    print(f"{item},")
