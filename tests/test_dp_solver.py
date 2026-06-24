import unittest
import sys
import os

# Asegurar que la carpeta raíz esté en el PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.graph import Graph
from core.dp_solver import DPSolver

class TestDPSolver(unittest.TestCase):
    def setUp(self):
        # Crear un grafo básico de prueba
        # Col 0: Nodo 1
        # Col 1: Nodo 2, Nodo 3
        # Col 2: Nodo 4
        self.graph = Graph()
        
        # Agregamos nodos (las coordenadas X influyen en el orden de reindexación)
        # Nodos ordenados por X de izquierda a derecha
        self.n1 = self.graph.add_node(x=100, y=200, columna=0) # ID 1
        self.n2 = self.graph.add_node(x=250, y=100, columna=1) # ID 2
        self.n3 = self.graph.add_node(x=250, y=300, columna=1) # ID 3
        self.n4 = self.graph.add_node(x=400, y=200, columna=2) # ID 4

        # Añadir aristas
        self.graph.add_edge(1, 2, 4)
        self.graph.add_edge(1, 3, 3)
        self.graph.add_edge(2, 4, 7)
        self.graph.add_edge(3, 4, 2)

    def test_regressive_min(self):
        response = DPSolver.solve_regressive(self.graph, mode="Min")
        self.assertEqual(response.total_cost, 5.0)
        self.assertEqual(response.path, [1, 3, 4])
        self.assertEqual(len(response.stages_tables), 2)

    def test_regressive_max(self):
        response = DPSolver.solve_regressive(self.graph, mode="Max")
        self.assertEqual(response.total_cost, 11.0)
        self.assertEqual(response.path, [1, 2, 4])

    def test_progressive_min(self):
        response = DPSolver.solve_progressive(self.graph, mode="Min")
        self.assertEqual(response.total_cost, 5.0)
        self.assertEqual(response.path, [1, 3, 4])
        self.assertEqual(len(response.vector_history), 4) # Inicial + Nodo 2 + Nodo 3 + Nodo 4

    def test_progressive_max(self):
        response = DPSolver.solve_progressive(self.graph, mode="Max")
        self.assertEqual(response.total_cost, 11.0)
        self.assertEqual(response.path, [1, 2, 4])

if __name__ == '__main__':
    unittest.main()
