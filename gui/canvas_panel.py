import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Optional
from core.graph import Node, Edge

class CanvasPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Configuración del Canvas
        self.canvas_width = 800
        self.canvas_height = 500
        self.num_columns = 5
        self.margin_x = 80
        self.node_radius = 20
        
        # Estado de interacción
        self.dragged_node: Optional[Node] = None
        self.selected_origin_node: Optional[Node] = None
        self.highlighted_path = []  # Lista de IDs de nodos del camino óptimo
        
        # Componentes visuales
        self._init_ui()

    def _init_ui(self):
        # Frame superior para controles del Canvas
        self.control_frame = tk.Frame(self, bg="#f5f6f8", height=40)
        self.control_frame.pack(fill=tk.X)
        self.control_frame.pack_propagate(False)
        
        # Instrucciones de uso rápidas
        self.info_label = tk.Label(
            self.control_frame, 
            text="Clic: Crear nodo | Doble Clic: Eliminar nodo | Arrastrar: Mover | Clic en Nodo A y luego en Nodo B: Conectar",
            bg="#f5f6f8", fg="#5f6368", font=("Helvetica", 9, "italic")
        )
        self.info_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Botón para limpiar canvas
        self.btn_clear = tk.Button(
            self.control_frame, text="Limpiar Lienzo", 
            command=self.clear_canvas,
            bg="#f1f3f4", fg="#3c4043", relief=tk.FLAT, 
            font=("Helvetica", 9, "bold"), cursor="hand2",
            padx=10, activebackground="#e8eaed"
        )
        self.btn_clear.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Canvas interactivo
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=1, highlightbackground="#dadce0")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindeos de eventos del Canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<ButtonPress-1>", self.on_node_press)
        self.canvas.bind("<B1-Motion>", self.on_node_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_node_release)
        self.canvas.bind("<Configure>", self.on_resize)

    def get_column_x(self, col: int) -> float:
        """Retorna el centro X para una columna dada."""
        if self.num_columns <= 1:
            return self.canvas_width / 2
        col_spacing = (self.canvas_width - 2 * self.margin_x) / (self.num_columns - 1)
        return self.margin_x + col * col_spacing

    def get_closest_column(self, x: float) -> int:
        """Encuentra el índice de la columna más cercana a una coordenada X."""
        best_col = 0
        min_dist = float('inf')
        for col in range(self.num_columns):
            col_x = self.get_column_x(col)
            dist = abs(x - col_x)
            if dist < min_dist:
                min_dist = dist
                best_col = col
        return best_col

    def find_node_at(self, x: float, y: float) -> Optional[Node]:
        """Busca un nodo visual bajo las coordenadas dadas."""
        for node in self.controller.graph.nodes.values():
            dist = ((node.x - x)**2 + (node.y - y)**2)**0.5
            if dist <= self.node_radius:
                return node
        return None

    def on_resize(self, event):
        """Maneja el redimensionamiento del canvas para acomodar el grafo."""
        self.canvas_width = event.width
        self.canvas_height = event.height
        
        # Re-ajustar las coordenadas X de los nodos de acuerdo con el nuevo ancho
        # (para mantener las proporciones y las columnas)
        graph = self.controller.graph
        if graph.nodes:
            for node in graph.nodes.values():
                node.x = self.get_column_x(node.columna)
                
        self.redraw()

    def on_canvas_click(self, event):
        # Evitar crear nodo si se hizo clic sobre uno existente
        node = self.find_node_at(event.x, event.y)
        if node is not None:
            return
            
        # Si había un nodo de origen seleccionado para conectar, deseleccionar
        if self.selected_origin_node:
            self.selected_origin_node = None
            self.redraw()
            return
            
        # Si el clic es en un espacio vacío, creamos un nuevo nodo
        # Determinar columna por la posición X
        col = self.get_closest_column(event.x)
        x_aligned = self.get_column_x(col)
        
        # Validar límites de Y
        y_clamped = max(self.node_radius + 10, min(event.y, self.canvas_height - self.node_radius - 10))
        
        # Crear nodo en el modelo
        self.controller.add_node_interactively(x_aligned, y_clamped, col)
        
        # Notificar cambio al controlador
        self.notify_change()

    def on_canvas_double_click(self, event):
        node = self.find_node_at(event.x, event.y)
        if node:
            # Confirmar eliminación si tiene aristas conectadas
            has_edges = any(e.origin.id == node.id or e.dest.id == node.id for e in self.controller.graph.edges)
            if has_edges:
                ans = messagebox.askyesno(
                    "Confirmar eliminación", 
                    f"¿Está seguro de que desea eliminar el Nodo {node.id}? Se borrarán todas sus aristas conectadas."
                )
                if not ans:
                    return
            
            # Borrar nodo en el modelo (reindexa automáticamente)
            self.controller.remove_node(node.id)
            self.selected_origin_node = None
            self.dragged_node = None
            self.notify_change()

    def on_node_press(self, event):
        node = self.find_node_at(event.x, event.y)
        if node:
            # Iniciar arrastre
            self.dragged_node = node
            
            # Lógica de conexión de aristas
            if self.selected_origin_node is None:
                self.selected_origin_node = node
                self.redraw()
            elif self.selected_origin_node.id != node.id:
                # Conectar el nodo seleccionado previamente con el actual
                origin = self.selected_origin_node
                dest = node
                
                # Validar sentido izquierda a derecha
                if origin.x >= dest.x:
                    messagebox.showerror(
                        "Error de Conexión", 
                        "Las aristas dirigidas deben ir estrictamente de izquierda a derecha."
                    )
                    self.selected_origin_node = None
                    self.redraw()
                    return
                    
                # Preguntar por el peso
                weight = simpledialog.askfloat(
                    "Peso de la Arista", 
                    f"Ingrese el peso para la arista dirigida ({origin.id} -> {dest.id}):",
                    parent=self, minvalue=-99999.0, maxvalue=99999.0
                )
                
                if weight is not None:
                    try:
                        self.controller.add_edge(origin.id, dest.id, weight)
                        self.notify_change()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
                        
                self.selected_origin_node = None
                self.redraw()
            else:
                # Si hace clic sobre el mismo origen seleccionado, lo deselecciona
                self.selected_origin_node = None
                self.redraw()

    def on_node_drag(self, event):
        if self.dragged_node:
            # Mover visualmente el nodo (feedback en tiempo real)
            # Clampear a límites del Canvas
            x = max(self.node_radius + 5, min(event.x, self.canvas_width - self.node_radius - 5))
            y = max(self.node_radius + 10, min(event.y, self.canvas_height - self.node_radius - 10))
            
            self.dragged_node.x = x
            self.dragged_node.y = y
            self.redraw()

    def on_node_release(self, event):
        if self.dragged_node:
            # Al soltar el nodo, aplicar el snapping a la columna más cercana
            col = self.get_closest_column(self.dragged_node.x)
            self.dragged_node.columna = col
            self.dragged_node.x = self.get_column_x(col)
            
            # Reindexar porque su orden en X puede haber cambiado
            self.controller.graph.reindex_nodes()
            
            self.dragged_node = None
            self.notify_change()

    def clear_canvas(self):
        if messagebox.askyesno("Limpiar Grafo", "¿Está seguro de que desea vaciar por completo el grafo actual?"):
            self.controller.clear_graph()
            self.selected_origin_node = None
            self.dragged_node = None
            self.highlighted_path = []
            self.notify_change()

    def set_highlighted_path(self, path):
        self.highlighted_path = path
        self.redraw()

    def notify_change(self):
        # Limpiar el camino resaltado ya que el grafo cambió
        self.highlighted_path = []
        self.redraw()
        # Notificar a la vista externa (ej. actualizar la caja de texto)
        # Esto se coordinará a través del controlador/main_window
        if hasattr(self.master, "on_graph_modified"):
            self.master.on_graph_modified()

    def redraw(self):
        self.canvas.delete("all")
        
        # 1. Dibujar las columnas de las etapas
        for col in range(self.num_columns):
            x = self.get_column_x(col)
            # Línea vertical punteada
            self.canvas.create_line(x, 10, x, self.canvas_height - 10, dash=(4, 4), fill="#dadce0", width=1.5)
            # Etiqueta de la etapa
            self.canvas.create_text(
                x, self.canvas_height - 15, 
                text=f"Etapa {col}", fill="#80868b", 
                font=("Helvetica", 9, "bold")
            )
            
        graph = self.controller.graph
        
        # 2. Dibujar aristas
        for edge in graph.edges:
            origin_id = edge.origin.id
            dest_id = edge.dest.id
            
            # Comprobar si esta arista pertenece a la ruta óptima
            is_in_path = False
            if self.highlighted_path and len(self.highlighted_path) > 1:
                # Comprobar si origin y dest son consecutivos en la lista
                for idx in range(len(self.highlighted_path) - 1):
                    if self.highlighted_path[idx] == origin_id and self.highlighted_path[idx+1] == dest_id:
                        is_in_path = True
                        break
            
            color = "#1a73e8" if is_in_path else "#9aa0a6"
            width = 3 if is_in_path else 1.5
            
            # Dibujar la arista dirigida (flecha al final)
            self.canvas.create_line(
                edge.origin.x, edge.origin.y, edge.dest.x, edge.dest.y, 
                arrow=tk.LAST, fill=color, width=width, arrowshape=(12, 14, 4)
            )
            
            # Escribir el peso en el centro de la arista
            mid_x = (edge.origin.x + edge.dest.x) / 2
            mid_y = (edge.origin.y + edge.dest.y) / 2
            
            # Formatear el peso
            w_str = str(int(edge.weight)) if edge.weight.is_integer() else f"{edge.weight:.2f}"
            
            # Rectángulo de fondo blanco para el texto del peso para hacerlo legible
            text_id = self.canvas.create_text(mid_x, mid_y, text=w_str, font=("Helvetica", 9, "bold"), fill=color)
            bbox = self.canvas.bbox(text_id)
            # Crear fondo de texto
            rect_id = self.canvas.create_rectangle(
                bbox[0]-3, bbox[1]-2, bbox[2]+3, bbox[3]+2, 
                fill="#ffffff", outline=""
            )
            # Mover el texto por encima del fondo
            self.canvas.tag_raise(text_id, rect_id)

        # 3. Dibujar nodos
        if graph.nodes:
            max_id = max(graph.nodes.keys())
            
            for node in graph.nodes.values():
                # Colores según el rol del nodo
                is_selected = self.selected_origin_node and self.selected_origin_node.id == node.id
                is_in_path = node.id in self.highlighted_path
                
                # Borde del nodo
                outline_color = "#1a73e8" if is_in_path else "#5f6368"
                outline_width = 3 if (is_selected or is_in_path) else 1.5
                
                if is_selected:
                    outline_color = "#f9ab00"  # Amarillo/dorado para selección
                    
                # Fondo del nodo
                if node.id == 1:
                    # Nodo inicial - Verde premium
                    fill_color = "#e6f4ea"
                    text_color = "#137333"
                    outline_color = "#137333" if not is_selected else "#f9ab00"
                elif node.id == max_id:
                    # Nodo final - Rojo/Coral premium
                    fill_color = "#fce8e6"
                    text_color = "#c5221f"
                    outline_color = "#c5221f" if not is_selected else "#f9ab00"
                else:
                    # Nodo intermedio
                    fill_color = "#f1f3f4"
                    text_color = "#3c4043"
                    
                # Dibujar el círculo
                self.canvas.create_oval(
                    node.x - self.node_radius, node.y - self.node_radius,
                    node.x + self.node_radius, node.y + self.node_radius,
                    fill=fill_color, outline=outline_color, width=outline_width
                )
                
                # Dibujar el texto del índice en el centro
                self.canvas.create_text(
                    node.x, node.y, 
                    text=str(node.id), fill=text_color, 
                    font=("Helvetica", 11, "bold")
                )
