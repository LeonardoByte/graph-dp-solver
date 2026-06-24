from typing import List, Dict, Any, Optional
from core.graph import Graph, Node, Edge

class RegressiveResponse:
    def __init__(self, path: List[int], total_cost: float, stages_tables: List[Dict[str, Any]]):
        self.path = path
        self.total_cost = total_cost
        self.stages_tables = stages_tables  # Lista de tablas por etapa (de atrás hacia adelante)

    def __repr__(self):
        return f"RegressiveResponse(cost={self.total_cost}, path={self.path})"


class ProgressiveResponse:
    def __init__(self, path: List[int], total_cost: float, vector_history: List[Dict[str, Any]], final_vector: Dict[int, Dict[str, Any]]):
        self.path = path
        self.total_cost = total_cost
        self.vector_history = vector_history  # Historial del vector por cada paso
        self.final_vector = final_vector      # Estado final del vector

    def __repr__(self):
        return f"ProgressiveResponse(cost={self.total_cost}, path={self.path})"


class DPSolver:
    @staticmethod
    def solve_regressive(graph: Graph, mode: str = "Min") -> RegressiveResponse:
        """
        Resuelve el problema de programación dinámica regresiva (de atrás hacia adelante).
        Divide el grafo en niveles verticales (Etapas) basados en la propiedad 'columna' de los nodos.
        """
        # Validar el grafo
        graph.validate(check_consecutive_columns=True)
        
        # Obtener columnas
        max_col = graph.get_max_column()
        if max_col == 0:
            raise ValueError("El grafo debe tener al menos dos columnas/etapas para ser resuelto.")
            
        # Agrupar nodos por columna
        nodes_by_col = {}
        for col in range(max_col + 1):
            nodes_by_col[col] = [n for n in graph.nodes.values() if n.columna == col]
            if not nodes_by_col[col]:
                raise ValueError(f"La columna {col} no tiene nodos asignados.")
                
        # Verificar que el nodo inicial (ID 1) esté en la columna 0
        if graph.nodes[1].columna != 0:
            raise ValueError("El nodo inicial (índice 1) debe estar en la primera columna (columna 0).")
            
        # El nodo final es el de ID máximo
        final_node_id = max(graph.nodes.keys())
        final_node = graph.nodes[final_node_id]
        if final_node.columna != max_col:
            raise ValueError(f"El nodo final (índice {final_node_id}) debe estar en la última columna (columna {max_col}).")

        # Diccionario para almacenar el óptimo acumulado de cada nodo
        # acumulado[node_id] = costo
        acumulado = {final_node_id: 0.0}
        
        # Historial de tablas por etapa (de atrás hacia adelante)
        stages_tables = []
        
        # Diccionario de decisiones óptimas para reconstruir el camino
        # decisiones[node_id] = siguiente_node_id
        decisiones = {}

        # Resolver de atrás hacia adelante (de la etapa max_col - 1 a la 0)
        # La etapa K conecta la columna K con la columna K+1
        for k in range(max_col - 1, -1, -1):
            col_origen = k
            col_destino = k + 1
            
            nodos_origen = sorted(nodes_by_col[col_origen], key=lambda n: n.id)
            nodos_destino = sorted(nodes_by_col[col_destino], key=lambda n: n.id)
            
            table_data = {}  # {u_id: {v_id: details}}
            optima = {}      # {u_id: {'costo': c, 'decision': v_id}}
            
            for u in nodos_origen:
                table_data[u.id] = {}
                best_val = float('inf') if mode == "Min" else float('-inf')
                best_dest = None
                
                # Buscar conexiones de u a cualquier v en la columna destino
                for v in nodos_destino:
                    # Encontrar arista u -> v
                    edge = next((e for e in graph.edges if e.origin.id == u.id and e.dest.id == v.id), None)
                    
                    if edge is not None and v.id in acumulado:
                        peso = edge.weight
                        acum_v = acumulado[v.id]
                        suma = peso + acum_v
                        table_data[u.id][v.id] = {
                            "peso": peso,
                            "acumulado_siguiente": acum_v,
                            "suma": suma,
                            "valido": True
                        }
                        
                        # Evaluar óptimo
                        if mode == "Min":
                            if suma < best_val:
                                best_val = suma
                                best_dest = v.id
                        else:  # Max
                            if suma > best_val:
                                best_val = suma
                                best_dest = v.id
                    else:
                        table_data[u.id][v.id] = {
                            "peso": None,
                            "acumulado_siguiente": None,
                            "suma": None,
                            "valido": False
                        }
                
                # Guardar el óptimo de la fila
                if best_dest is not None:
                    optima[u.id] = {
                        "costo": best_val,
                        "decision": best_dest
                    }
                    acumulado[u.id] = best_val
                    decisiones[u.id] = best_dest
                else:
                    optima[u.id] = {
                        "costo": float('inf') if mode == "Min" else float('-inf'),
                        "decision": None
                    }
            
            # Guardar estructura de la tabla de la etapa
            stages_tables.append({
                "stage": k,
                "nodos_origen": [u.id for u in nodos_origen],
                "nodos_destino": [v.id for v in nodos_destino],
                "table_data": table_data,
                "optima": optima
            })

        # Reconstruir el camino óptimo a partir del nodo 1
        path = [1]
        curr = 1
        while curr in decisiones:
            curr = decisiones[curr]
            path.append(curr)
            if curr == final_node_id:
                break
                
        # Verificar si alcanzamos el nodo final
        if path[-1] != final_node_id:
            raise ValueError("No existe un camino continuo de principio a fin utilizando transiciones válidas.")
            
        total_cost = acumulado[1]
        
        # Como iteramos hacia atrás, invertimos las tablas para mostrarlas de la etapa 0 a la última
        stages_tables.reverse()
        
        return RegressiveResponse(path, total_cost, stages_tables)

    @staticmethod
    def solve_progressive(graph: Graph, mode: str = "Min") -> ProgressiveResponse:
        """
        Resuelve el problema de programación dinámica progresiva (de adelante hacia atrás)
        en base al orden topológico (índices ordenados).
        """
        # Validar el grafo (de forma general: izquierda a derecha)
        graph.validate(check_consecutive_columns=False)
        
        n = len(graph.nodes)
        final_node_id = max(graph.nodes.keys())
        
        # Inicializar vector caminos
        # caminos[nodo_id] = {"padre": id, "acumulado": costo}
        caminos = {}
        for nid in graph.nodes.keys():
            if nid == 1:
                caminos[nid] = {"padre": None, "acumulado": 0.0}
            else:
                caminos[nid] = {
                    "padre": None, 
                    "acumulado": float('inf') if mode == "Min" else float('-inf')
                }
                
        vector_history = []
        
        # Guardar estado inicial (solo procesado el origen)
        vector_history.append({
            "step_node": 1,
            "comparisons": {},
            "vector_state": {nid: dict(caminos[nid]) for nid in caminos}
        })
        
        # Procesar los nodos en orden consecutivo de 2 a N
        sorted_node_ids = sorted(graph.nodes.keys())
        
        for nid in sorted_node_ids:
            if nid == 1:
                continue
                
            node = graph.nodes[nid]
            comparisons = {}
            best_val = float('inf') if mode == "Min" else float('-inf')
            best_parent = None
            
            # Buscar aristas entrantes p -> nid
            entrantes = [e for e in graph.edges if e.dest.id == nid]
            
            for edge in entrantes:
                p_id = edge.origin.id
                peso = edge.weight
                acum_p = caminos[p_id]["acumulado"]
                
                # Comprobar si el padre es alcanzable
                is_reachable = acum_p != float('inf') and acum_p != float('-inf')
                
                if is_reachable:
                    suma = acum_p + peso
                    comparisons[p_id] = {
                        "acumulado_padre": acum_p,
                        "peso_arista": peso,
                        "suma": suma,
                        "valido": True
                    }
                    
                    if mode == "Min":
                        if suma < best_val:
                            best_val = suma
                            best_parent = p_id
                    else:  # Max
                        if suma > best_val:
                            best_val = suma
                            best_parent = p_id
                else:
                    comparisons[p_id] = {
                        "acumulado_padre": acum_p,
                        "peso_arista": peso,
                        "suma": None,
                        "valido": False
                    }
            
            # Actualizar vector para este nodo si se encontró un camino alcanzable
            if best_parent is not None:
                caminos[nid] = {"padre": best_parent, "acumulado": best_val}
            
            # Registrar paso
            vector_history.append({
                "step_node": nid,
                "comparisons": comparisons,
                "vector_state": {k: dict(caminos[k]) for k in caminos}
            })
            
        # Reconstruir el camino óptimo hacia atrás desde el nodo final
        if caminos[final_node_id]["acumulado"] in (float('inf'), float('-inf')):
            raise ValueError("El nodo final no es alcanzable desde el nodo inicial.")
            
        path = []
        curr = final_node_id
        while curr is not None:
            path.append(curr)
            curr = caminos[curr]["padre"]
            
        path.reverse()
        
        # Verificar que el camino comience en 1
        if path[0] != 1:
            raise ValueError("No se pudo construir una ruta válida que empiece en el nodo inicial 1.")
            
        total_cost = caminos[final_node_id]["acumulado"]
        
        return ProgressiveResponse(path, total_cost, vector_history, caminos)
