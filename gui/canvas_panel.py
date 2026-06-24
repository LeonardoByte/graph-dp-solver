import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Optional
from core.graph import Node, Edge

class CanvasPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        
        # Dimensiones fijas virtuales del Canvas (scrollable)
        self.canvas_width = 1200
        self.canvas_height = 800
        self.num_columns = 11
        self.margin_x = 80
        self.node_radius = 20
        
        # Estado de interacción
        self.dragged_node: Optional[Node] = None
        self.selected_origin_node: Optional[Node] = None
        self.highlighted_path = []  # Lista de IDs de nodos del camino óptimo
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.has_dragged = False
        
        self._init_ui()

    def _init_ui(self):
        # Frame superior para controles del Canvas
        self.control_frame = tk.Frame(self, bg="#f5f6f8", height=40)
        self.control_frame.pack(fill=tk.X)
        self.control_frame.pack_propagate(False)
        
        # Instrucciones de uso rápidas
        self.info_label = tk.Label(
            self.control_frame, 
            text="Clic vacío: Crear nodo | Arrastrar: Mover | Clic A y luego B: Conectar | Doble Clic: Eliminar",
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
        
        # Contenedor del Canvas y barras de desplazamiento
        canvas_container = tk.Frame(self, bg="#ffffff")
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.v_scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas interactivo con scrollregion fija
        self.canvas = tk.Canvas(
            canvas_container, 
            bg="#ffffff", 
            highlightthickness=1, 
            highlightbackground="#dadce0",
            scrollregion=(0, 0, self.canvas_width, self.canvas_height),
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # Bindings de eventos del Canvas coordinados para evitar conflictos
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

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
        """Busca un nodo visual bajo las coordenadas absolutas en el lienzo."""
        for node in self.controller.graph.nodes.values():
            dist = ((node.x - x)**2 + (node.y - y)**2)**0.5
            if dist <= self.node_radius:
                return node
        return None

    def on_press(self, event):
        # Convertir coordenadas relativas del evento en coordenadas absolutas del lienzo (con scroll)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        node = self.find_node_at(x, y)
        if node:
            # Clic sobre un nodo: iniciar posible arrastre o conexión
            self.dragged_node = node
            self.drag_start_x = x
            self.drag_start_y = y
            self.has_dragged = False
            
            # Lógica de conexión de aristas
            if self.selected_origin_node is None:
                self.selected_origin_node = node
                self.redraw()
            elif self.selected_origin_node.id != node.id:
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
                # Clic en el mismo origen: deseleccionar
                self.selected_origin_node = None
                self.redraw()
        else:
            # Clic en vacío: deseleccionar origen y crear un nodo nuevo de inmediato
            self.selected_origin_node = None
            
            # Determinar columna por la posición X
            col = self.get_closest_column(x)
            x_aligned = self.get_column_x(col)
            
            # Validar límites de Y en el canvas virtual
            y_clamped = max(self.node_radius + 10, min(y, self.canvas_height - self.node_radius - 10))
            
            # Crear nodo en el modelo
            self.controller.add_node_interactively(x_aligned, y_clamped, col)
            self.notify_change()

    def on_drag(self, event):
        if self.dragged_node:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            self.has_dragged = True
            
            # Mover visualmente el nodo (feedback en tiempo real)
            x_clamped = max(self.node_radius + 5, min(x, self.canvas_width - self.node_radius - 5))
            y_clamped = max(self.node_radius + 10, min(y, self.canvas_height - self.node_radius - 10))
            
            self.dragged_node.x = x_clamped
            self.dragged_node.y = y_clamped
            self.redraw()

    def on_release(self, event):
        if self.dragged_node:
            if self.has_dragged:
                # Al soltar el nodo tras arrastre, aplicar el snapping
                col = self.get_closest_column(self.dragged_node.x)
                self.dragged_node.columna = col
                self.dragged_node.x = self.get_column_x(col)
                
                # Reindexar porque su orden en X puede haber cambiado
                self.controller.graph.reindex_nodes()
                self.notify_change()
                
            self.dragged_node = None
            self.has_dragged = False

    def on_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        node = self.find_node_at(x, y)
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
        self.highlighted_path = []
        self.redraw()
        # Notificar a MainWindow para propagar la actualización mutua
        if hasattr(self.master, "on_graph_modified"):
            self.master.on_graph_modified()
        elif hasattr(self.master.master, "on_graph_modified"):
            self.master.master.on_graph_modified()

    def redraw(self):
        self.canvas.delete("all")
        
        # 1. Dibujar las columnas de las etapas
        for col in range(self.num_columns):
            x = self.get_column_x(col)
            # Línea vertical punteada en todo el alto virtual
            self.canvas.create_line(x, 10, x, self.canvas_height - 10, dash=(4, 4), fill="#dadce0", width=1.5)
            # Etiqueta de la etapa
            self.canvas.create_text(
                x, self.canvas_height - 20, 
                text=f"Etapa {col}", fill="#80868b", 
                font=("Helvetica", 10, "bold")
            )
            
        graph = self.controller.graph
        
        # 2. Dibujar aristas
        for edge in graph.edges:
            origin_id = edge.origin.id
            dest_id = edge.dest.id
            
            is_in_path = False
            if self.highlighted_path and len(self.highlighted_path) > 1:
                for idx in range(len(self.highlighted_path) - 1):
                    if self.highlighted_path[idx] == origin_id and self.highlighted_path[idx+1] == dest_id:
                        is_in_path = True
                        break
            
            color = "#1a73e8" if is_in_path else "#9aa0a6"
            width = 3 if is_in_path else 1.5
            
            self.canvas.create_line(
                edge.origin.x, edge.origin.y, edge.dest.x, edge.dest.y, 
                arrow=tk.LAST, fill=color, width=width, arrowshape=(12, 14, 4)
            )
            
            mid_x = (edge.origin.x + edge.dest.x) / 2
            mid_y = (edge.origin.y + edge.dest.y) / 2
            
            w_str = str(int(edge.weight)) if edge.weight.is_integer() else f"{edge.weight:.2f}"
            
            text_id = self.canvas.create_text(mid_x, mid_y, text=w_str, font=("Helvetica", 9, "bold"), fill=color)
            bbox = self.canvas.bbox(text_id)
            rect_id = self.canvas.create_rectangle(
                bbox[0]-3, bbox[1]-2, bbox[2]+3, bbox[3]+2, 
                fill="#ffffff", outline=""
            )
            self.canvas.tag_raise(text_id, rect_id)

        # 3. Dibujar nodos
        if graph.nodes:
            max_id = max(graph.nodes.keys())
            
            for node in graph.nodes.values():
                is_selected = self.selected_origin_node and self.selected_origin_node.id == node.id
                is_in_path = node.id in self.highlighted_path
                
                outline_color = "#1a73e8" if is_in_path else "#5f6368"
                outline_width = 3 if (is_selected or is_in_path) else 1.5
                
                if is_selected:
                    outline_color = "#f9ab00"
                    
                if node.id == 1:
                    fill_color = "#e6f4ea"
                    text_color = "#137333"
                    outline_color = "#137333" if not is_selected else "#f9ab00"
                elif node.id == max_id:
                    fill_color = "#fce8e6"
                    text_color = "#c5221f"
                    outline_color = "#c5221f" if not is_selected else "#f9ab00"
                else:
                    fill_color = "#f1f3f4"
                    text_color = "#3c4043"
                    
                self.canvas.create_oval(
                    node.x - self.node_radius, node.y - self.node_radius,
                    node.x + self.node_radius, node.y + self.node_radius,
                    fill=fill_color, outline=outline_color, width=outline_width
                )
                
                self.canvas.create_text(
                    node.x, node.y, 
                    text=str(node.id), fill=text_color, 
                    font=("Helvetica", 11, "bold")
                )
