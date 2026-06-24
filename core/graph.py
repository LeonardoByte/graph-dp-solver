class Node:
    def __init__(self, node_id: int, x: float, y: float, columna: int = 0):
        self.id = node_id
        self.x = x
        self.y = y
        self.columna = columna

    def __repr__(self):
        return f"Node({self.id}, col={self.columna}, x={self.x}, y={self.y})"


class Edge:
    def __init__(self, origin: Node, dest: Node, weight: float):
        self.origin = origin
        self.dest = dest
        self.weight = weight

    def __repr__(self):
        return f"Edge({self.origin.id} -> {self.dest.id}, weight={self.weight})"


class Graph:
    def __init__(self):
        self.nodes = {}  # {node_id: Node}
        self.edges = []  # List[Edge]

    def add_node(self, x: float, y: float, columna: int = 0) -> Node:
        # Generar un ID temporal
        new_id = len(self.nodes) + 1
        while new_id in self.nodes:
            new_id += 1
        node = Node(new_id, x, y, columna)
        self.nodes[new_id] = node
        self.reindex_nodes()
        return node

    def remove_node(self, node_id: int):
        if node_id in self.nodes:
            # Eliminar aristas asociadas
            self.edges = [e for e in self.edges if e.origin.id != node_id and e.dest.id != node_id]
            # Eliminar nodo
            del self.nodes[node_id]
            # Reindexar nodos
            self.reindex_nodes()

    def add_edge(self, origin_id: int, dest_id: int, weight: float) -> Edge:
        if origin_id not in self.nodes or dest_id not in self.nodes:
            raise ValueError("Los nodos de origen y destino deben existir en el grafo.")
        
        origin = self.nodes[origin_id]
        dest = self.nodes[dest_id]
        
        # Validar dirección izquierda a derecha
        if origin.x >= dest.x:
            raise ValueError("Las aristas deben dirigirse estrictamente de izquierda a derecha.")
            
        # Validar aristas duplicadas
        for edge in self.edges:
            if edge.origin.id == origin_id and edge.dest.id == dest_id:
                # Si ya existe, actualizamos el peso
                edge.weight = weight
                return edge
                
        new_edge = Edge(origin, dest, weight)
        self.edges.append(new_edge)
        return new_edge

    def remove_edge(self, origin_id: int, dest_id: int):
        self.edges = [e for e in self.edges if not (e.origin.id == origin_id and e.dest.id == dest_id)]

    def reindex_nodes(self):
        """
        Reordena todos los nodos basándose principalmente en su posición X (de izquierda a derecha).
        Si empatan en X, se ordenan según su posición Y (de arriba a abajo).
        Actualiza los diccionarios internos y los IDs de los nodos para que sean 1, 2, ..., N.
        """
        if not self.nodes:
            return

        # Obtener lista de nodos y ordenarlos por X, luego por Y
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: (n.x, n.y))
        
        # Reasignar IDs
        new_nodes = {}
        for index, node in enumerate(sorted_nodes, start=1):
            node.id = index
            new_nodes[index] = node
            
        self.nodes = new_nodes

    def clear(self):
        self.nodes.clear()
        self.edges.clear()

    def validate(self, check_consecutive_columns: bool = False):
        """
        Valida las aristas del grafo.
        - De forma general, que no haya ciclos o aristas de derecha a izquierda.
        - Si check_consecutive_columns es True, valida que las aristas solo vayan de la columna K a la columna K+1.
        """
        if not self.nodes:
            raise ValueError("El grafo está vacío.")
            
        # Comprobar que existe el nodo 1 (origen)
        if 1 not in self.nodes:
            raise ValueError("Debe existir un nodo inicial con índice 1.")
            
        # Comprobar si hay aristas de derecha a izquierda
        for edge in self.edges:
            if edge.origin.x >= edge.dest.x:
                raise ValueError(
                    f"Arista inválida: {edge.origin.id} -> {edge.dest.id}. "
                    "Todas las conexiones deben ir estrictamente de izquierda a derecha."
                )
            if check_consecutive_columns:
                if edge.dest.columna != edge.origin.columna + 1:
                    raise ValueError(
                        f"Para la resolución regresiva por etapas, las conexiones deben ser entre columnas consecutivas. "
                        f"Arista {edge.origin.id} (Col {edge.origin.columna}) -> {edge.dest.id} (Col {edge.dest.columna}) no es consecutiva."
                    )
                    
        # Comprobar conectividad básica: el nodo final debe ser alcanzable (opcional en validación básica, pero útil)
        max_id = max(self.nodes.keys())
        if max_id == 1 and len(self.nodes) > 1:
            raise ValueError("El nodo final debe ser el de índice más alto y debe ser diferente del inicial.")

    def get_max_column(self) -> int:
        if not self.nodes:
            return 0
        return max(n.columna for n in self.nodes.values())
