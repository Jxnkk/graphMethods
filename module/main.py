import math
import json 

def analyze_graph(graph):
    operations = graph["operations"]
    links = graph["links"]
    y_values = []
    x_values = []
    angle_values = []
    touching_pairs = []
    nodes_and_operations = []
    node_count = 0
    nodes_blocked = 0
    backwards_links = 0
    stackings = 0
    intersections = 0
    improper_stacking = 0
    excessive_nodes = 0

    def get_y_value(operation_name):
        for op in operations:
            if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
                return op["position"]["y"]
        return None

    def get_x_value(operation_name):
        for op in operations:
            if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
                return op["position"]["x"]
        return None

    def get_inputs(operation_name):
        for op in operations:
            if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
                return op["inputs"]
        return None

    def get_outputs(operation_name):
        for op in operations:
            if op["name"] == operation_name and op["type"] == "PRIMITIVE_OPERATION":
                return op["outputs"]
        return None

    def get_inputs_this():
        return [input["name"] for input in graph.get("inputs", [])]
    
    def get_outputs_this():
        return [output["name"] for output in graph.get("output", [])]

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

        y += 50 + (data_location * 50)
        return {"x": x, "y": y}

    def find_greatest_x(data):
        max_x = 0
        isOperation = False

        for group in data:
            for idx, item in enumerate(group):
                if "x" in item:
                    if item["x"] > max_x:
                        max_x = item["x"]
                        if (idx == 0 or idx == len(group) - 1) and (group[0].get("operation") != "this" and group[-1].get("operation") != "this"):
                            isOperation = True
                        else:
                            isOperation = False
                
        if isOperation:
            x += 285
        return max_x
    
    def find_greatest_y(data):
        max_y = 0
        isOperation = False
        operationName = ""

        for group in data:
            for idx, item in enumerate(group):
                if "y" in item:
                    if item["y"] > max_y:
                        max_y = item["y"]
                        if idx == 0 and group[0]["operation"] != "this":
                            isOperation = True
                            operationName = group[0]["operation"]
                        elif idx == len(group) - 1 and group[-1]["operation"] != "this":
                            isOperation = True
                            operationName = group[-1]["operation"]
                        else:
                            isOperation = False
        if isOperation:
            greatest_y = x_y_range(operationName)[3]

        return max_y

    def get_location_this(data, type):
        x = 0
        y = 87.5

        if type == "source":
            i_o = get_inputs_this()
        else:
            x = find_greatest_x(nodes_and_operations)
            x += 200
            i_o = get_outputs_this()

        data_location = 0
        for box in i_o:
            if box != data:
                data_location += 1
            else:
                break

        y += 50 + (data_location * 50)
        return {"x": x, "y": y}

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

    def are_mirrored_opx(op1, op2, middle, x_threshold, y_threshold):
        left_x = op1["position"]["x"]
        right_x = op2["position"]["x"]
        mirrored_x = abs((middle - left_x) - (right_x - middle)) <= x_threshold
        mirrored_y = abs(op1["position"]["y"] - op2["position"]["y"]) <= y_threshold

        return mirrored_x and mirrored_y
    
    def are_mirrored_opy(op1, op2, middle, y_threshold, x_threshold):
        top_y = op1["position"]["y"]
        bottom_y = op2["position"]["y"]
        mirrored_y = abs((middle - top_y) - (bottom_y - middle)) <= y_threshold
        mirrored_x = abs(op1["position"]["x"] - op2["position"]["x"]) <= x_threshold

        return mirrored_y and mirrored_x

    def x_y_range(operation_name):
        range_list = []
        x1 = get_x_value(operation_name)
        y1 = get_y_value(operation_name)
        range_list.append(x1)
        inputs = len(get_inputs(operation_name))
        outputs = len(get_outputs(operation_name))
        s = max(inputs, outputs)
        x2 = x1 + 285
        range_list.append(x2)
        range_list.append(y1)
        y2 = y1 + 45 + (s * 45)
        range_list.append(y2)
        return range_list
    
    def operation_symmetry(type, middle, threshold1, threshold2):
        operations1 = []
        operations2 = []

        for op in operations:
            if op["type"] != "PRIMITIVE_OPERATION":
                continue

            range_vals = x_y_range(op["name"])
            if type == "x":
                start = range_vals[0]
                end = range_vals[1]
            else:
                start = range_vals[2]
                end = range_vals[3]

            if start <= middle <= end:
                operations1.append(op)
                operations2.append(op)
            elif op["position"][type] <= middle:
                operations1.append(op)
            else:
                operations2.append(op)

        if len(operations1) == 0 or len(operations2) == 0:
            return 0, 0

        operation_count_symmetry = min(len(operations1) / len(operations2), len(operations2) / len(operations1))

        operation_mirror_symmetry = 0
        for op1 in operations1:
            for op2 in operations2:
                if type == "x" and are_mirrored_opx(op1, op2, middle, threshold1, threshold2):
                    operation_mirror_symmetry += 1
                    break
                elif type == "y" and are_mirrored_opy(op1, op2, middle, threshold2, threshold1):
                    operation_mirror_symmetry += 1
                    break

        operation_mirror_symmetry /= min(len(operations1), len(operations2))
        return round(operation_count_symmetry, 2), round(operation_mirror_symmetry, 2)

    def are_mirrored_nodex(node1, node2, middle, x_threshold, y_threshold):
        left_x = node1["x"]
        right_x = node2["x"]
        mirrored_x = abs((middle - left_x) - (right_x - middle)) <= x_threshold
        mirrored_y = abs(node1["y"] - node2["y"]) <= y_threshold

        return mirrored_x and mirrored_y
    
    def are_mirrored_nodey(node1, node2, middle, y_threshold, x_threshold):
        top_y = node1["y"]
        bottom_y = node2["y"]
        mirrored_y = abs((middle - top_y) - (bottom_y - middle)) <= y_threshold
        mirrored_x = abs(node1["x"] - node2["x"]) <= x_threshold

        return mirrored_y and mirrored_x

    def node_symmetry(type, middle, threshold1, threshold2):
        nodes1 = []
        nodes2 = [] 
        
        for link in links:
            for point in link["control_points"]:
                if type == "x":
                    location = point["x"]
                else:
                    location = point["y"]
                if location <= middle:
                    nodes1.append(point)
                else:
                    nodes2.append(point)

        if len(nodes1) == 0 or len(nodes2) == 0:
            return 0.0, 0.0
    
        node_count_symmetry = min(len(nodes1) / len(nodes2), len(nodes2) / len(nodes1))
        node_mirror_symmetry = 0
        for node1 in nodes1:
            for node2 in nodes2:
                if type == "x" and are_mirrored_nodex(node1, node2, middle, threshold1, threshold2):
                    node_mirror_symmetry += 1
                    break
                elif type == "y" and are_mirrored_nodey(node1, node2, middle, threshold2, threshold1):
                    node_mirror_symmetry += 1
                    break

        node_mirror_symmetry /= min(len(nodes1), len(nodes2))
        return round(node_count_symmetry, 2), round(node_mirror_symmetry, 2)
    
    def find_clustering(type, threshold_1, threshold_2):
        deduction = 0
        if type == "x":
            groups = eliminate_similar(find_alignment(x_values, threshold_1), threshold_2)
        else:
            groups = eliminate_similar(find_alignment(y_values, threshold_2), threshold_1)
        
        allLinks = []
        for i in range(len(groups[0]) - 1):
            currentLinks = []
            for link in links:
                for point in link["control_points"]:
                    if type == "x" and groups[0][i] <= point["x"] <= groups[0][i + 1]:
                        currentLinks.append(link)
                    elif type == "y" and groups[0][i] <= point["y"] <= groups[0][i + 1]:
                        currentLinks.append(link)
            allLinks.append(currentLinks)

        for i in range(len(allLinks)):
            maxLinks = max(1, int((groups[0][i + 1] - groups[0][i])/75))
            if len(allLinks[i]) > maxLinks:
                deduction -= 1
        return deduction 

    def boxes_touch(op1_name, op2_name):
        x1a, x2a, y1a, y2a = x_y_range(op1_name)
        x1b, x2b, y1b, y2b = x_y_range(op2_name)
        return (x1a < x2b and x2a > x1b) and (y1a < y2b and y2a > y1b)

    def number_of_unique_angles(angles, rounding_factor):
        rounded_angles = [round(abs(angle) / rounding_factor) * rounding_factor for angle in angles]
        unique_angles = set(rounded_angles)
        return len(unique_angles)

    def calculate_slope(p1, p2):
        if p1["x"] - p2["x"] == 0:
            return 0.0 
        return (p1["y"] - p2["y"]) / (p1["x"] - p2["x"])

    def segments_intersection(p1, p2, p3, p4, source1, source2, sink1, sink2, threshold, threshold2):
        slope_1 = calculate_slope(p1, p2)
        slope_2 = calculate_slope(p3, p4)

        x_min, x_second, x_third, x_max = sorted([p1["x"], p2["x"], p3["x"], p4["x"]])
        y_min, y_second, y_third, y_max = sorted([p1["y"], p2["y"], p3["y"], p4["y"]])
        x_location = [x_min in [p1["x"], p2["x"]], x_second in [p3["x"], p4["x"]], x_third in [p3["x"], p4["x"]], x_max in [p1["x"], p2["x"]]]
        y_location = [y_min in [p1["y"], p2["y"]], y_second in [p3["y"], p4["y"]], y_third in [p3["y"], p4["y"]], y_max in [p1["y"], p2["y"]]]
        valid_location_combinations = [[True, True, False, False], [False, False, True, True], [False, True, False, True]]
        if x_location not in valid_location_combinations or y_location not in valid_location_combinations:
            return "Nothing"
        
        if source1 != source2 and slope_1 * slope_2 < 0:
            return "Intersection"

        if slope_1 * slope_2 > 0 and abs(abs(slope_1) - abs(slope_2)) <= threshold and x_location in valid_location_combinations[:2] and y_location in valid_location_combinations[:2]:
            if source1 == source2:
                return "Stacking"
            else:
                return "Improper Stacking"

        return "Nothing"

    def get_subsegments(link):
        pts = [pt for pt in link if "x" in pt and "y" in pt]
        return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

    def compute_final_score():
        total_ops = len([op for op in operations if op["type"] == "PRIMITIVE_OPERATION"])
        total_links = len(links)
        max_alignment = total_ops
        max_spacing = total_ops
        x_align = len(find_alignment(x_values, 25))
        y_align = len(find_alignment(y_values, 25))
        x_spacing = spacing_uniformity(find_alignment(x_values, 25), 25)
        y_spacing = spacing_uniformity(find_alignment(y_values, 25), 25)
        touching = len(touching_pairs)
        unique_angles = number_of_unique_angles(angle_values, 10)
        directionality_score = round(1 - (backwards_links / total_links), 2) if total_links else 1
        stacking_score = round(1 - (improper_stacking / total_links), 2) if total_links else 1
        spacing_score = round(((x_spacing + y_spacing) / (2 * max_spacing)), 2) if max_spacing else 1
        alignment_score = round(((x_align + y_align) / (2 * max_alignment)), 2) if max_alignment else 1
        angle_score = round(1 - (unique_angles / len(angle_values)), 2) 
        touching_score = round(1 - (touching / total_ops**2), 2) if total_ops > 1 else 1  #Compare against possible pairs
        symmetry_score = round(sum([op_count_symmetry1, op_count_symmetry2, op_mirror_symmetry1, op_mirror_symmetry2, node_count_symmetry1, node_count_symmetry2, node_mirror_symmetry1, node_mirror_symmetry2])/8, 2)
        excessive_node_score = round(1 - (node_count / total_links), 2) if total_links else 1
        x_clustering_deduction = find_clustering("x", 25, 50)
        y_clustering_deduction = find_clustering("y", 25, 50)
        if excessive_node_score < 0:
            excessive_node_score = 0
        final_score = round((
        0.10 * directionality_score +     
        0.35 * stacking_score +          
        0.05 * spacing_score +            
        0.10 * alignment_score +         
        0.10 * angle_score +              
        0.15 * touching_score +           
        0.15 * excessive_node_score +     
        0.05 * symmetry_score
        ) * 100, 2) + x_clustering_deduction + y_clustering_deduction - improper_stacking - nodes_blocked
        return {
            "Final Score": final_score,
            "Directionality Score": directionality_score,
            "Stacking Score": stacking_score,
            "Spacing Score": spacing_score, 
            "Alignment Score": alignment_score,
            "Angle Score": angle_score,
            "Touching Score": touching_score,
            "Node Score": excessive_node_score,
            "Symmetry Score": symmetry_score,
            "Clustering Deduction": x_clustering_deduction + y_clustering_deduction,
            "Improper Stacking Deduction": improper_stacking,
            "Nodes Blocked Deduction": nodes_blocked
        }

    for op in operations:
        if op["type"] == "PRIMITIVE_OPERATION":
            x_values.append(op["position"]["x"])
            y_values.append(op["position"]["y"])
    
    for link in links:
        source_name = link["source"]["operation"]
        sink_name = link["sink"]["operation"]
        source_data = link["source"]["data"]
        sink_data = link["sink"]["data"]
        source_x = get_x_value(source_name)
        sink_x = get_x_value(sink_name)
        if source_x is not None and sink_x is not None:
            if sink_x < source_x + 285:
                backwards_links += 1

        nodes = link["control_points"]
        if len(nodes) > 4:
            excessive_nodes += 1
        nao = [{"operation": source_name, "data": source_data}]
        if source_name != "this":
            nao.append(get_location_operation(source_name, source_data, "source"))
        else:
            nao.append(get_location_this(source_data, "source"))
        for node in nodes:
            node_count += 1
            nao.append(node)
            for op in operations:
                if op["type"] == "PRIMITIVE_OPERATION":
                    op_area = x_y_range(op["name"])
                    if op_area[0] <= node["x"] <= op_area[1] and op_area[2] <= node["y"] <= op_area[3]:
                        nodes_blocked += 1
        if sink_name != "this":
            nao.append(get_location_operation(sink_name, sink_data, "sink"))
        else:
            nao.append(get_location_this(source_data, "sink"))
        nao.append({"operation": sink_name, "data": sink_data})
        nodes_and_operations.append(nao)

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

    for i in range(len(operations)):
        for j in range(i + 1, len(operations)):
            op1 = operations[i]
            op2 = operations[j]
            if op1["type"] == "PRIMITIVE_OPERATION" and op2["type"] == "PRIMITIVE_OPERATION":
                if boxes_touch(op1["name"], op2["name"]):
                    touching_pairs.append((op1["name"], op2["name"]))
            
    greatest_x = find_greatest_x(nodes_and_operations)
    greatest_x += 200
    middle1 = greatest_x/2
    greatest_y= find_greatest_y(nodes_and_operations)
    greatest_y += 300
    middle2 = greatest_y/2
    op_count_symmetry1, op_mirror_symmetry1 = operation_symmetry("x", middle1, 100, 10)
    op_count_symmetry2, op_mirror_symmetry2 = operation_symmetry("y", middle2, 100, 10)
    node_count_symmetry1, node_mirror_symmetry1 = node_symmetry("x", middle1, 50, 10)
    node_count_symmetry2, node_mirror_symmetry2 = node_symmetry("y", middle2, 50, 10)

    for i in range(len(nodes_and_operations)):
        segs_i = get_subsegments(nodes_and_operations[i])
        for j in range(i + 1, len(nodes_and_operations)):
            segs_j = get_subsegments(nodes_and_operations[j])
            for (A, B) in segs_i:
                for (C, D) in segs_j:
                    result = segments_intersection(A, B, C, D, nodes_and_operations[i][0], nodes_and_operations[j][0], nodes_and_operations[i][-1], nodes_and_operations[j][-1], 25, 0.25)
                    if result != "Nothing":
                        if result == "Intersection":
                            intersections += 1
                        elif result == "Stacking":
                            stackings += 1
                        else:
                            improper_stacking += 1
    
    grading = compute_final_score()

    results = {
        "Total Operations": len(operations),
        "Operations X Alignment": len(find_alignment(x_values, 25)),
        "Operations Y Alignment": len(find_alignment(y_values, 25)),
        "Operation X Spacing Uniformity": spacing_uniformity(find_alignment(x_values, 25), 25),
        "Operation Y Spacing Uniformity": spacing_uniformity(find_alignment(y_values, 25), 25),
        "Number of Touching Operations": len(touching_pairs),
        "Total Links": len(links),
        "Backwards Links": backwards_links,
        "Total Angles": len(angle_values),
        "Unique Angles": number_of_unique_angles(angle_values, 5),
        "Total Stacking": stackings,
        "Improper Stacking": improper_stacking,
        "Total Nodes": node_count,
        "Nodes Blocked": nodes_blocked,
        "Operation Count X Symmetry": op_count_symmetry1, 
        "Operation Count Y Symmetry": op_count_symmetry2, 
        "Operation Mirror X Symmetry": op_mirror_symmetry1, 
        "Operation Mirror Y Symmetry": op_mirror_symmetry2, 
        "Node Count X Symmetry": node_count_symmetry1, 
        "Node Count Y Symmetry": node_count_symmetry2, 
        "Node Mirror X Symmetry": node_mirror_symmetry1, 
        "Node Mirror Y Symmetry": node_mirror_symmetry2, 
        "Final Score": round(grading["Final Score"], 2),
        "Directionality Score": grading["Directionality Score"],
        "Stacking Score": grading["Stacking Score"],
        "Spacing Score": grading["Spacing Score"],
        "Alignment Score": grading["Alignment Score"],
        "Angle Score": grading["Angle Score"],
        "Touching Score": grading["Touching Score"],
        "Node Score": grading["Node Score"],
        "Symmetry Score": grading["Symmetry Score"],
        "Clustering Deduction": grading["Clustering Deduction"],
        "Improper Stacking Deduction": grading["Improper Stacking Deduction"] * -1,
        "Nodes Blocked Deduction": grading["Nodes Blocked Deduction"] * -1
    }
    
    return results

with open("test_graph/graph_mrq051mc.json", "r") as f:
    graph = json.load(f)
    print("Final Score:", analyze_graph(graph)["Final Score"])
    print("Stacking Score:", analyze_graph(graph)["Stacking Score"])
    print("Directionality Score:", analyze_graph(graph)["Directionality Score"])
    print("Spacing Score:", analyze_graph(graph)["Spacing Score"])
    print("Alignment Score:", analyze_graph(graph)["Alignment Score"])
    print("Touching Score:", analyze_graph(graph)["Touching Score"])
    print("Angle Score:", analyze_graph(graph)["Angle Score"])
    print("Node Score:", analyze_graph(graph)["Node Score"])
    print("Symmetry Score:", analyze_graph(graph)["Symmetry Score"])
    print("Clustering Deduction:", analyze_graph(graph)["Clustering Deduction"])
    print("Improper Stacking Deduction:", analyze_graph(graph)["Improper Stacking Deduction"])
    print("Nodes Blocked Deduction:", analyze_graph(graph)["Nodes Blocked Deduction"])



    