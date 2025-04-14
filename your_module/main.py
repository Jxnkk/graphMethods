import math
import json

with open("test_graph/graph_pcdarulg.json", "r") as f:
    graph = json.load(f)

operations = graph["operations"]
links = graph["links"]
y_values = []
x_values = []
angle_values = []
touching_pairs = []
nodes_and_operations = []
common_h_distance = 0
common_v_distance = 0
total_angles = 0
angles_of_45 = 0
node_count = 0
nodes_blocked = 0
backwards_links = 0
excessive_nodes = 0
stacking = 0
proper_stacking = 0
improper_stacking = 0

#Getting the y value of an operation's location given operation name (X and y are the left and top most coordinate of the graph)
def get_y_value(operation_name):
    for op in operations:
        if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
            return op["position"]["y"]
    return None

#Getting the x value of an operation's location given operation name
def get_x_value(operation_name):
    for op in operations:
        if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
            return op["position"]["x"]
    return None

#Gets inputs of an operation
def get_inputs(operation_name):
    for op in operations:
        if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
            return op["inputs"]
    return None

#Gets outputs of an operation
def get_outputs(operation_name):
    for op in operations:
        if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
            return op["outputs"]
    return None

#Prints location of a specific input or output of an operation
def get_location_operation(operation_name, data, type):
    x = get_x_value(operation_name)
    y = get_y_value(operation_name)

    if type == "source":
        x += 285
        i_o = get_outputs(operation_name)
    else:
        x += 10
        i_o = get_inputs(operation_name)

    data_location = 0
    for input in i_o:
      if input != data:
        data_location += 1
      else:
        break

    y += 45 + (data_location * 45)
    return {"x": x, "y": y}

#Eliminates similar numbers within a certain threshold and returns how many were removed
def eliminate_similar(numbers, threshold):
    numbers.sort()
    result = []
    counts = []

    if not numbers:
        return result, counts
    current = numbers[0]
    count = 1
    for i in range(1, len(numbers)):
        if abs(numbers[i] - current) < threshold:
            count += 1
        else:
            result.append(current)
            counts.append(count)
            current = numbers[i]
            count = 1

    result.append(current)
    counts.append(count)
    return result, counts

#Calculates slope given two points
def compute_slope(p1, p2):
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    if dy != 0:
        return dx/dy
    else:
        return 0

#Finds how many are aligned vertically and horizontally with a threshold of error and compares it how far away from other horizontal and vertical groups
def find_alignment(values, threshold):
    firstNumber = True
    alignment_list = []
    values.sort()

    for i in range(1, len(values)):
        if abs(values[i] - values[i - 1]) <= threshold:
          if firstNumber:
            alignment_list.append(values[i - 1])
            alignment_list.append(values[i])
            firstNumber = False
          else:
            alignment_list.append(values[i])
        else:
            firstNumber = True
    return alignment_list

#Finds how many operations have common horizontal and vertical spacing
def spacing_uniformity(values, threshold):
    spacing_uniformity = 0
    unique_locations, removed = eliminate_similar(values, threshold)
    diffs = []
    added_indices = set()

    if len(unique_locations) > 1:
        for i in range(1, len(unique_locations)):
            diffs.append(abs(unique_locations[i] - unique_locations[i - 1]))
        avg_diff = sum(diffs) / len(diffs)
        for i in range(len(diffs)):
            if abs(diffs[i] - avg_diff) <= threshold:
                if i not in added_indices:
                    spacing_uniformity += removed[i]
                    added_indices.add(i)
                if (i + 1) not in added_indices:
                    spacing_uniformity += removed[i + 1]
                    added_indices.add(i + 1)

    else:
        spacing_uniformity = len(values)

    return spacing_uniformity

#Returns the x and y range for an operation (See if any operations are touching and are blocking nodes)
def x_y_range(operation_name):
    range_list = []
    x1 = get_x_value(operation_name)
    y1 = get_y_value(operation_name)
    range_list.append(x1)
    inputs = len(get_inputs(operation_name))
    outputs = len(get_outputs(operation_name))
    s = 1
    if(inputs >= outputs):
        s = inputs
    else:
        s = outputs
    x2 = x1 + 285
    range_list.append(x2)
    range_list.append(y1)
    y2 =  y1 + 45 + (s * 45)
    range_list.append(y2)
    return range_list

def boxes_touch(op1_name, op2_name):
    # Get box ranges for both operations
    x1a, x2a, y1a, y2a = x_y_range(op1_name)
    x1b, x2b, y1b, y2b = x_y_range(op2_name)

    # Check if rectangles overlap in both x and y
    overlap_x = x1a < x2b and x2a > x1b
    overlap_y = y1a < y2b and y2a > y1b

    return overlap_x and overlap_y

#Adds all operation x values into x_values list
for op in operations:
    if op["type"] == "PRIMITIVE_OPERATION":
        x_values.append(op["position"]["x"])

#Adds all operation y values into y_values list
for op in operations:
    if op["type"] == "PRIMITIVE_OPERATION":
        y_values.append(op["position"]["y"])

for link in links:
    #Checks if sink operation is located to the left of the source operation
    source_name = link["source"]["operation"]
    sink_name = link["sink"]["operation"]
    source_data = link["source"]["data"]
    sink_data = link["sink"]["data"]
    source_x = get_x_value(source_name)
    sink_x = get_x_value(sink_name)
    if not source_x == None and not sink_x == None:
        if sink_x < source_x + 285:
            backwards_links += 1
    #Detecting nodes are behind operations (Not very efficient because of the for loops but works)
    nodes = link["control_points"]
    if(len(nodes) > 4):
      excessive_nodes += 1
    nao = []
    nao.append({"operation" : source_name, "data" : source_data})
    if source_name != "this":
        nao.append(get_location_operation(source_name, source_data, "source"))
    for node in nodes:
        node_count += 1
        nao.append(node)
        for op in operations:
            if op["type"] == "PRIMITIVE_OPERATION":
                operation_area = x_y_range(op["name"])
                if operation_area[0] <= node["x"] and operation_area[1] >= node["x"] and operation_area[2] <= node["y"] and operation_area[3] >= node["y"]:
                    nodes_blocked += 1
    if sink_name != "this":
        nao.append(get_location_operation(sink_name, sink_data, "sink"))
    nao.append({"operation" : sink_name, "data" : sink_data})
    nodes_and_operations.append(nao)

#Finds angles nodes make
for nao in nodes_and_operations:
    if len(nao) >= 4:
        for i in range(2, len(nao) - 2):
            p1, p2, p3 = nao[i - 1], nao[i], nao[i + 1]
            d12 = math.hypot(p2["x"] - p1["x"], p2["y"] - p1["y"])
            d23 = math.hypot(p3["x"] - p2["x"], p3["y"] - p2["y"])
            d31 = math.hypot(p3["x"] - p1["x"], p3["y"] - p1["y"])
            if 2 * d12 * d23 != 0:
                cos_angle = (d12**2 + d23**2 - d31**2)/(2 * d12 * d23)
            else:
                cos_angle = 0
            angle = math.degrees(math.acos(cos_angle))
            if p1["x"] >= p3["x"]:
                angle = -angle
            angle_values.append(angle)

#Finds how many angles are close to being a multiple of 45 with a deviation of 5 (We could simplfy this later if deviation isn't necessary)
for angle in angle_values:
    normalized_angle = angle % 360
    lower_multiple = (normalized_angle // 45) * 45
    upper_multiple = lower_multiple + 45

    deviation_lower = abs(normalized_angle - lower_multiple)
    deviation_upper = abs(normalized_angle - upper_multiple)
    min_deviation = min(deviation_lower, deviation_upper)
    if min_deviation == deviation_lower:
      multiple = lower_multiple
    else:
      multiple = upper_multiple

    if min_deviation <= 5: #Change 5 if you want lower or higher tolerance
        angles_of_45 += 1

#Finds a list of touching operations;
for i in range(len(operations)):
    for j in range(i + 1, len(operations)):
        op1 = operations[i]
        op2 = operations[j]
        if op1["type"] == "PRIMITIVE_OPERATION" and op2["type"] == "PRIMITIVE_OPERATION":
            if boxes_touch(op1["name"], op2["name"]):
                touching_pairs.append((op1["name"], op2["name"]))

print("Total Operations:", len(operations))
print("Operations X Alignment:", len(find_alignment(x_values, 25)))
print("Operations Y Alignment:", len(find_alignment(y_values, 25)))
print("Operation X Spacing Uniformity:", spacing_uniformity(find_alignment(x_values, 25), 25))
print("Operation Y Spacing Uniformity:", spacing_uniformity(find_alignment(y_values, 25), 25))
print("Number of Touching Operations:", len(touching_pairs))
print("------------------------------------------------------------------------------------------")
print("Total Links:", len(links))
print("Angles of 45:", angles_of_45)
print("Backwards Links:", backwards_links)
print("Total Stacking:", stacking)
print("Improper Stacking (Fully covered links or stacked from different source operations):", improper_stacking)
print("Proper Stacking:", proper_stacking)
print("------------------------------------------------------------------------------------------")
print("Total Nodes:", node_count)
print("Nodes Blocked:", nodes_blocked)
print("Excessive Nodes:", excessive_nodes)
print("------------------------------------------------------------------------------------------")