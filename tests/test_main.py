import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import unittest
import json
from module.main import analyze_graph  

class TestGraphAnalysis(unittest.TestCase):
    def test_graph_analysis1(self):
        with open("test_graph/graph_pcdarulg.json", "r") as f:
            graph = json.load(f)

        result = analyze_graph(graph)

        self.assertEqual(result["Total Operations"], 10)
        self.assertEqual(result["Operations X Alignment"], 8)
        self.assertEqual(result["Operations Y Alignment"], 5)
        self.assertEqual(result["Number of Touching Operations"], 0)
        self.assertEqual(result["Total Links"], 20)
        self.assertEqual(result["Backwards Links"], 0)
        self.assertEqual(result["Total Stacking"], 14)
        self.assertEqual(result["Improper Stacking"], 0)
        self.assertEqual(result["Total Nodes"], 15)
        self.assertEqual(result["Nodes Blocked"], 0)
    
    def test_graph_analysis2(self):
        with open("test_graph/graph_mrq051mc.json", "r") as f:
            graph = json.load(f)

        result = analyze_graph(graph)

        self.assertEqual(result["Total Operations"], 7)
        self.assertEqual(result["Operations X Alignment"], 2)
        self.assertEqual(result["Operations Y Alignment"], 7)
        self.assertEqual(result["Number of Touching Operations"], 0)
        self.assertEqual(result["Total Links"], 11)
        self.assertEqual(result["Backwards Links"], 0)
        self.assertEqual(result["Total Stacking"], 5)
        self.assertEqual(result["Improper Stacking"], 0)
        self.assertEqual(result["Total Nodes"], 13)
        self.assertEqual(result["Nodes Blocked"], 2)

    def test_graph_analysis3(self):
        with open("test_graph/graph_grz8c41o.json", "r") as f:
            graph = json.load(f)

        result = analyze_graph(graph)

        self.assertEqual(result["Total Operations"], 9)
        self.assertEqual(result["Operations X Alignment"], 8)
        self.assertEqual(result["Operations Y Alignment"], 4)
        self.assertEqual(result["Number of Touching Operations"], 0)
        self.assertEqual(result["Total Links"], 15)
        self.assertEqual(result["Backwards Links"], 1)
        self.assertEqual(result["Total Stacking"], 6)
        self.assertEqual(result["Improper Stacking"], 2)
        self.assertEqual(result["Total Nodes"], 9)
        self.assertEqual(result["Nodes Blocked"], 1)

        
    def test_graph_analysis4(self):
        with open("test_graph/graph_c3boljl0.json", "r") as f:
            graph = json.load(f)

        result = analyze_graph(graph)

        self.assertEqual(result["Total Operations"], 6)
        self.assertEqual(result["Operations X Alignment"], 4)
        self.assertEqual(result["Operations Y Alignment"], 4)
        self.assertEqual(result["Number of Touching Operations"], 1)
        self.assertEqual(result["Total Links"], 7)
        self.assertEqual(result["Backwards Links"], 2)
        self.assertEqual(result["Total Stacking"], 0)
        self.assertEqual(result["Improper Stacking"], 0)
        self.assertEqual(result["Total Nodes"], 7)
        self.assertEqual(result["Nodes Blocked"], 1)

if __name__ == '__main__':
    unittest.main()

