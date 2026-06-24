import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
from core.graph import Graph, Node, Edge
from core.dp_solver import DPSolver, RegressiveResponse, ProgressiveResponse

class GraphController:
    def __init__(self):
        self.graph = Graph()
        self.mode = "Min"  # "Min" o "Max"
        self.history_dir = "historial_grafos"

    def clear_graph(self):
        self.graph.clear()

    def add_node_interactively(self, x: float, y: float, columna: int) -> Node:
        """
        Agrega un nodo interactivo. Asume que la columna ya ha sido
        determinada por la zona del canvas donde se hizo clic o soltó.
        """
        node = self.graph.add_node(x, y, columna)
        return node

    def remove_node(self, node_id: int):
        self.graph.remove_node(node_id)

    def add_edge(self, origin_id: int, dest_id: int, weight: float) -> Edge:
        return self.graph.add_edge(origin_id, dest_id, weight)

    def remove_edge(self, origin_id: int, dest_id: int):
        self.graph.remove_edge(origin_id, dest_id)

    def set_mode(self, mode: str):
        if mode in ("Min", "Max"):
            self.mode = mode

    def load_from_text(self, text_data: str):
        """
        Parsea y carga un grafo desde texto en formato:
        origen destino peso
        """
        self.clear_graph()
        
        lines = text_data.strip().split("\n")
        parsed_edges = []
        node_ids = set()
        
        # 1. Parsear y validar formato línea por línea
        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
                
            parts = re.split(r'\s+', line)
            if len(parts) != 3:
                raise ValueError(
                    f"Error en la línea {i}: '{line}'. "
                    "Debe contener exactamente 3 valores separados por espacios (origen destino peso)."
                )
                
            try:
                u_id = int(parts[0])
                v_id = int(parts[1])
                weight = float(parts[2])
            except ValueError:
                raise ValueError(
                    f"Error en la línea {i}: '{line}'. "
                    "Los índices de nodos deben ser enteros y el peso un número decimal/entero."
                )
                
            if u_id <= 0 or v_id <= 0:
                raise ValueError(
                    f"Error en la línea {i}: '{line}'. "
                    "Los índices de los nodos deben ser enteros positivos mayores que 0."
                )
                
            if u_id == v_id:
                raise ValueError(
                    f"Error en la línea {i}: '{line}'. "
                    "No se permiten bucles (aristas de un nodo a sí mismo)."
                )
                
            # Verificar aristas duplicadas en el texto
            for prev_u, prev_v, _ in parsed_edges:
                if prev_u == u_id and prev_v == v_id:
                    raise ValueError(
                        f"Error en la línea {i}: Arista duplicada {u_id} -> {v_id}."
                    )
                    
            parsed_edges.append((u_id, v_id, weight))
            node_ids.add(u_id)
            node_ids.add(v_id)

        if not parsed_edges:
            raise ValueError("El texto no contiene ninguna definición de arista válida.")

        if 1 not in node_ids:
            raise ValueError("Debe incluirse un nodo inicial con índice 1.")

        # 2. Determinar columnas (etapas) de los nodos para ubicarlos espacialmente
        # Algoritmo de camino más largo (longest path) desde el nodo 1
        columnas = {1: 0}
        
        # Inicializar los demás nodos en columna 0
        for nid in node_ids:
            if nid != 1:
                columnas[nid] = 0
                
        # Iterar para calcular la columna máxima (capas)
        n_nodes = len(node_ids)
        for _ in range(n_nodes):
            cambios = False
            for u_id, v_id, _ in parsed_edges:
                # Si el nodo de origen ya ha sido alcanzado/tiene columna calculada
                if u_id in columnas:
                    nueva_col = columnas[u_id] + 1
                    if nueva_col > columnas[v_id]:
                        columnas[v_id] = nueva_col
                        cambios = True
            if not cambios:
                break
        else:
            # Si el bucle no terminó por break, significa que hay ciclos
            raise ValueError("El grafo contiene ciclos dirigidos (no es un Grafo Dirigido Acíclico - DAG).")

        # 3. Crear los nodos en el modelo con coordenadas automáticas
        # Ancho y alto de referencia para el dibujo
        W_canvas = 750
        H_canvas = 450
        
        max_col = max(columnas.values())
        dX = W_canvas / (max_col + 2) if max_col > 0 else W_canvas / 2
        
        # Agrupar nodos por columna para calcular Y
        nodes_by_col = {}
        for nid, col in columnas.items():
            if col not in nodes_by_col:
                nodes_by_col[col] = []
            nodes_by_col[col].append(nid)
            
        # Crear los nodos en el modelo y guardar referencias
        created_nodes = {}
        for col, nids in nodes_by_col.items():
            nids.sort()
            K = len(nids)
            dY = H_canvas / (K + 1)
            
            for index, nid in enumerate(nids, start=1):
                x = 80 + col * dX
                y = dY * index
                
                # Crear nodo en el modelo. Ojo: add_node de Graph reindexa internamente.
                # Para conservar los IDs del texto durante la carga y que las aristas coincidan, 
                # poblamos temporalmente los nodos directos en self.graph.nodes sin reindexar.
                node = Node(nid, x, y, col)
                self.graph.nodes[nid] = node
                created_nodes[nid] = node

        # 4. Crear las aristas en el modelo
        for u_id, v_id, weight in parsed_edges:
            # Validar que vaya de izquierda a derecha en X
            origin = self.graph.nodes[u_id]
            dest = self.graph.nodes[v_id]
            if origin.x >= dest.x:
                raise ValueError(
                    f"Arista inválida: {u_id} -> {v_id}. "
                    "Las aristas deben ir de izquierda a derecha visualmente. "
                    "Asegúrese de que el origen esté en una etapa anterior al destino."
                )
            self.add_edge(u_id, v_id, weight)
            
        # 5. Hacer una reindexación final y validación de consistencia
        self.graph.reindex_nodes()
        self.graph.validate()

    def get_text_representation(self) -> str:
        """
        Retorna la representación en texto plano del grafo actual en formato:
        origen destino peso
        """
        lines = []
        for edge in self.graph.edges:
            # El formato debe usar enteros para pesos enteros
            w = int(edge.weight) if edge.weight.is_integer() else edge.weight
            lines.append(f"{edge.origin.id} {edge.dest.id} {w}")
        return "\n".join(lines)

    def save_to_history(self, name: str = None) -> str:
        """
        Guarda el grafo actual en un archivo de texto en historial_grafos/
        Retorna el nombre del archivo creado.
        """
        if not self.graph.nodes:
            raise ValueError("No se puede guardar un grafo vacío.")
            
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
        # Validar el grafo antes de guardar
        self.graph.validate()
        
        # Generar nombre si no se suministra uno
        if not name or not name.strip():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"grafo_{timestamp}"
            
        # Asegurar extensión .txt
        if not name.endswith(".txt"):
            filename = f"{name}.txt"
        else:
            filename = name
            
        filepath = os.path.join(self.history_dir, filename)
        content = self.get_text_representation()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return filename

    def load_from_history(self, filename: str):
        """
        Carga un grafo desde la carpeta de historial
        """
        filepath = os.path.join(self.history_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filename} no existe en el historial.")
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.load_from_text(content)

    def get_history_list(self) -> List[str]:
        """
        Retorna una lista de los archivos de grafos guardados en el historial, ordenados por fecha (más recientes primero).
        """
        if not os.path.exists(self.history_dir):
            return []
            
        files = [f for f in os.listdir(self.history_dir) if f.endswith(".txt")]
        # Ordenar por fecha de modificación
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.history_dir, x)), reverse=True)
        return files

    def delete_from_history(self, filename: str):
        filepath = os.path.join(self.history_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def solve_regressive(self) -> RegressiveResponse:
        return DPSolver.solve_regressive(self.graph, self.mode)

    def solve_progressive(self) -> ProgressiveResponse:
        return DPSolver.solve_progressive(self.graph, self.mode)
