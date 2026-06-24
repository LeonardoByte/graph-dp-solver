import tkinter as tk
from tkinter import ttk, messagebox

class ScrollableFrame(tk.Frame):
    """Un frame contenedor con scrollbar vertical automático."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="#ffffff")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg="#ffffff")
        
        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Ajustar ancho del frame interno al del canvas
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Habilitar scroll con rueda del mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Desplazar solo si el canvas está visible y enfocado
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class RegressivePanel(tk.Frame):
    def __init__(self, parent, controller, canvas_panel_ref):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        self.canvas_panel = canvas_panel_ref
        
        self._init_ui()

    def _init_ui(self):
        # Panel superior de controles
        top_bar = tk.Frame(self, bg="#f5f6f8", height=50)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        title = tk.Label(
            top_bar, text="Programación Dinámica Regresiva (Etapas/Tablas)",
            font=("Helvetica", 11, "bold"), bg="#f5f6f8", fg="#202124"
        )
        title.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.btn_solve = tk.Button(
            top_bar, text="Resolver Grafo", command=self.solve,
            bg="#1a73e8", fg="#ffffff", relief=tk.FLAT,
            font=("Helvetica", 9, "bold"), cursor="hand2",
            padx=15, activebackground="#1557b0", activeforeground="#ffffff"
        )
        self.btn_solve.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Frame de Resultados Destacados (Ruta y Costo)
        self.result_frame = tk.Frame(self, bg="#e8f0fe", height=60, bd=1, relief=tk.SOLID, highlightbackground="#1a73e8")
        self.result_frame.pack(fill=tk.X, padx=15, pady=10)
        self.result_frame.pack_propagate(False)
        
        self.result_label = tk.Label(
            self.result_frame, 
            text="Haga clic en 'Resolver Grafo' para ver los resultados.",
            bg="#e8f0fe", fg="#1a73e8", font=("Helvetica", 10, "bold"),
            justify=tk.LEFT
        )
        self.result_label.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)

        # Contenedor scrollable para las tablas didácticas
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def solve(self):
        # Limpiar resultados anteriores
        for widget in self.scroll_frame.scrollable_content.winfo_children():
            widget.destroy()
            
        try:
            # Ejecutar el algoritmo regresivo
            response = self.controller.solve_regressive()
            
            # 1. Mostrar resultado final en el panel destacado
            path_str = " → ".join(map(str, response.path))
            cost_str = str(int(response.total_cost)) if response.total_cost.is_integer() else f"{response.total_cost:.2f}"
            obj_txt = "Mínimo" if self.controller.mode == "Min" else "Máximo"
            
            self.result_label.config(
                text=f"Ruta Óptima ({obj_txt}):  {path_str}\n"
                     f"Costo Acumulado Total:  {cost_str}"
            )
            
            # Resaltar la ruta en el canvas
            self.canvas_panel.set_highlighted_path(response.path)
            
            # 2. Dibujar las tablas didácticas de las etapas
            parent_frame = self.scroll_frame.scrollable_content
            
            for idx, stage_info in enumerate(response.stages_tables):
                stage_num = stage_info["stage"]
                nodos_origen = stage_info["nodos_origen"]
                nodos_destino = stage_info["nodos_destino"]
                table_data = stage_info["table_data"]
                optima = stage_info["optima"]
                
                # Contenedor de la etapa
                stage_card = tk.LabelFrame(
                    parent_frame, 
                    text=f" ETAPA {stage_num} (Conecta Columna {stage_num} con Columna {stage_num+1}) ",
                    font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#202124",
                    padx=10, pady=10, bd=1, relief=tk.SOLID
                )
                stage_card.pack(fill=tk.X, pady=10, padx=5)
                
                # Crear la matriz/grilla de la tabla
                grid_frame = tk.Frame(stage_card, bg="#dadce0", bd=1)
                grid_frame.pack(anchor="w", pady=5)
                
                # Encabezados de columna
                # Esquina vacía de la tabla (Fila \ Columna)
                lbl = tk.Label(grid_frame, text="Estado (u) \\ Destino (v)", font=("Helvetica", 9, "bold"), bg="#f1f3f4", width=22, height=2, bd=1, relief=tk.SOLID)
                lbl.grid(row=0, column=0, sticky="nsew")
                
                # Columnas de destino (nodos de la etapa siguiente)
                for col_idx, v_id in enumerate(nodos_destino, start=1):
                    lbl = tk.Label(grid_frame, text=f"Nodo {v_id}", font=("Helvetica", 9, "bold"), bg="#f1f3f4", width=15, height=2, bd=1, relief=tk.SOLID)
                    lbl.grid(row=0, column=col_idx, sticky="nsew")
                    
                # Columnas adicionales de óptimos
                lbl_opt_val = tk.Label(grid_frame, text="Costo Óptimo f*(u)", font=("Helvetica", 9, "bold"), bg="#e8f0fe", fg="#1a73e8", width=18, height=2, bd=1, relief=tk.SOLID)
                lbl_opt_val.grid(row=0, column=len(nodos_destino) + 1, sticky="nsew")
                
                lbl_opt_dec = tk.Label(grid_frame, text="Decisión Óptima v*", font=("Helvetica", 9, "bold"), bg="#e8f0fe", fg="#1a73e8", width=18, height=2, bd=1, relief=tk.SOLID)
                lbl_opt_dec.grid(row=0, column=len(nodos_destino) + 2, sticky="nsew")
                
                # Llenar las filas (nodos de origen)
                for row_idx, u_id in enumerate(nodos_origen, start=1):
                    # Nombre de la fila
                    lbl = tk.Label(grid_frame, text=f"Nodo {u_id}", font=("Helvetica", 9, "bold"), bg="#f8f9fa", width=22, height=2, bd=1, relief=tk.SOLID)
                    lbl.grid(row=row_idx, column=0, sticky="nsew")
                    
                    # Decisión óptima calculada para este nodo u
                    best_decision = optima[u_id]["decision"]
                    
                    # Celda de transición a cada destino v
                    for col_idx, v_id in enumerate(nodos_destino, start=1):
                        cell_info = table_data[u_id][v_id]
                        
                        if cell_info["valido"]:
                            peso = cell_info["peso"]
                            acum = cell_info["acumulado_siguiente"]
                            suma = cell_info["suma"]
                            
                            # Formatear números
                            peso_s = str(int(peso)) if peso.is_integer() else f"{peso:.1f}"
                            acum_s = str(int(acum)) if acum.is_integer() else f"{acum:.1f}"
                            suma_s = str(int(suma)) if suma.is_integer() else f"{suma:.1f}"
                            
                            text_cell = f"{peso_s} + {acum_s} = {suma_s}"
                            
                            # Resaltar en verde si es la decisión óptima elegida
                            bg_color = "#e6f4ea" if v_id == best_decision else "#ffffff"
                            fg_color = "#137333" if v_id == best_decision else "#3c4043"
                            weight_font = "bold" if v_id == best_decision else "normal"
                        else:
                            text_cell = "—"
                            bg_color = "#ffffff"
                            fg_color = "#9aa0a6"
                            weight_font = "normal"
                            
                        lbl = tk.Label(
                            grid_frame, text=text_cell, bg=bg_color, fg=fg_color, 
                            font=("Helvetica", 9, weight_font), bd=1, relief=tk.SOLID, height=2
                        )
                        lbl.grid(row=row_idx, column=col_idx, sticky="nsew")
                        
                    # Celdas del óptimo f*(u)
                    opt_val = optima[u_id]["costo"]
                    if opt_val in (float('inf'), float('-inf')):
                        opt_val_s = "No alc."
                    else:
                        opt_val_s = str(int(opt_val)) if opt_val.is_integer() else f"{opt_val:.2f}"
                        
                    lbl_val = tk.Label(
                        grid_frame, text=opt_val_s, bg="#e8f0fe", fg="#1a73e8", 
                        font=("Helvetica", 9, "bold"), bd=1, relief=tk.SOLID, height=2
                    )
                    lbl_val.grid(row=row_idx, column=len(nodos_destino) + 1, sticky="nsew")
                    
                    # Celda de decisión óptima v*
                    lbl_dec = tk.Label(
                        grid_frame, text=f"Ir a Nodo {best_decision}" if best_decision else "—", 
                        bg="#e8f0fe", fg="#1a73e8", font=("Helvetica", 9, "bold"), 
                        bd=1, relief=tk.SOLID, height=2
                    )
                    lbl_dec.grid(row=row_idx, column=len(nodos_destino) + 2, sticky="nsew")
                    
        except Exception as e:
            messagebox.showerror("Error al Resolver", str(e))


class ProgressivePanel(tk.Frame):
    def __init__(self, parent, controller, canvas_panel_ref):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        self.canvas_panel = canvas_panel_ref
        
        self._init_ui()

    def _init_ui(self):
        # Panel superior de controles
        top_bar = tk.Frame(self, bg="#f5f6f8", height=50)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        title = tk.Label(
            top_bar, text="Programación Dinámica Progresiva (Lineal/Orden Topológico)",
            font=("Helvetica", 11, "bold"), bg="#f5f6f8", fg="#202124"
        )
        title.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.btn_solve = tk.Button(
            top_bar, text="Resolver Grafo", command=self.solve,
            bg="#1a73e8", fg="#ffffff", relief=tk.FLAT,
            font=("Helvetica", 9, "bold"), cursor="hand2",
            padx=15, activebackground="#1557b0", activeforeground="#ffffff"
        )
        self.btn_solve.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Frame de Resultados Destacados (Ruta y Costo)
        self.result_frame = tk.Frame(self, bg="#e8f0fe", height=60, bd=1, relief=tk.SOLID, highlightbackground="#1a73e8")
        self.result_frame.pack(fill=tk.X, padx=15, pady=10)
        self.result_frame.pack_propagate(False)
        
        self.result_label = tk.Label(
            self.result_frame, 
            text="Haga clic en 'Resolver Grafo' para ver los resultados.",
            bg="#e8f0fe", fg="#1a73e8", font=("Helvetica", 10, "bold"),
            justify=tk.LEFT
        )
        self.result_label.pack(side=tk.LEFT, padx=15, fill=tk.BOTH, expand=True)

        # Contenedor scrollable para los pasos lineales
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def solve(self):
        # Limpiar resultados anteriores
        for widget in self.scroll_frame.scrollable_content.winfo_children():
            widget.destroy()
            
        try:
            # Ejecutar el algoritmo progresivo
            response = self.controller.solve_progressive()
            
            # 1. Mostrar resultado final en el panel destacado
            path_str = " → ".join(map(str, response.path))
            cost_str = str(int(response.total_cost)) if response.total_cost.is_integer() else f"{response.total_cost:.2f}"
            obj_txt = "Mínimo" if self.controller.mode == "Min" else "Máximo"
            
            self.result_label.config(
                text=f"Ruta Óptima ({obj_txt}):  {path_str}\n"
                     f"Costo Acumulado Total:  {cost_str}"
            )
            
            # Resaltar la ruta en el canvas
            self.canvas_panel.set_highlighted_path(response.path)
            
            # 2. Dibujar el paso a paso del vector lineal
            parent_frame = self.scroll_frame.scrollable_content
            
            # Dibujar tarjetas de paso para cada nodo procesado
            for step_idx, step in enumerate(response.vector_history):
                node_id = step["step_node"]
                comparisons = step["comparisons"]
                vector_state = step["vector_state"]
                
                # Tarjeta del paso
                step_card = tk.LabelFrame(
                    parent_frame, 
                    text=f" Paso {step_idx + 1}: Analizando Nodo {node_id} ",
                    font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#202124",
                    padx=12, pady=10, bd=1, relief=tk.SOLID
                )
                step_card.pack(fill=tk.X, pady=8, padx=5)
                
                # Si es el origen (nodo 1)
                if node_id == 1:
                    lbl = tk.Label(
                        step_card, 
                        text="• Nodo inicial del grafo. Costo acumulado base = 0.0 (Sin padre).",
                        bg="#ffffff", fg="#137333", font=("Helvetica", 9, "bold"), anchor="w"
                    )
                    lbl.pack(fill=tk.X, pady=2)
                else:
                    # Mostrar la pregunta proactiva
                    lbl_question = tk.Label(
                        step_card,
                        text="¿Cuál es el camino óptimo desde el origen hasta mí mismo?",
                        font=("Helvetica", 9, "bold", "italic"), bg="#ffffff", fg="#3c4043", anchor="w"
                    )
                    lbl_question.pack(fill=tk.X, pady=(0, 5))
                    
                    # Detalle de comparaciones con padres
                    if not comparisons:
                        lbl_no_parents = tk.Label(
                            step_card, text="  No tiene padres directos (Nodo no alcanzable).",
                            font=("Helvetica", 9), bg="#ffffff", fg="#c5221f", anchor="w"
                        )
                        lbl_no_parents.pack(fill=tk.X)
                    else:
                        # Determinar cuál es el mejor padre del nodo actual
                        best_parent = vector_state[node_id]["padre"]
                        
                        for p_id, comp in comparisons.items():
                            if comp["valido"]:
                                acum_p = comp["acumulado_padre"]
                                peso = comp["peso_arista"]
                                suma = comp["suma"]
                                
                                # Formatear números
                                acum_s = str(int(acum_p)) if acum_p.is_integer() else f"{acum_p:.1f}"
                                peso_s = str(int(peso)) if peso.is_integer() else f"{peso:.1f}"
                                suma_s = str(int(suma)) if suma.is_integer() else f"{suma:.1f}"
                                
                                is_best = (p_id == best_parent)
                                comp_txt = f"  - Vía Padre {p_id}: Costo acum. {acum_s} + Peso arista {peso_s} = {suma_s}"
                                
                                if is_best:
                                    comp_txt += "  ← [ÓPTIMO SELECCIONADO]"
                                    color_fg = "#137333"
                                    font_w = "bold"
                                else:
                                    color_fg = "#5f6368"
                                    font_w = "normal"
                            else:
                                peso = comp["peso_arista"]
                                peso_s = str(int(peso)) if peso.is_integer() else f"{peso:.1f}"
                                comp_txt = f"  - Vía Padre {p_id}: Costo acum. Infinito + Peso arista {peso_s} = Inalcanzable"
                                color_fg = "#9aa0a6"
                                font_w = "normal"
                                
                            lbl_comp = tk.Label(
                                step_card, text=comp_txt, font=("Helvetica", 9, font_w),
                                bg="#ffffff", fg=color_fg, anchor="w"
                            )
                            lbl_comp.pack(fill=tk.X, pady=1)

                # Mostrar el estado del vector lineal caminos[] en este paso
                vector_frame = tk.Frame(step_card, bg="#f8f9fa", bd=1, relief=tk.SOLID)
                vector_frame.pack(fill=tk.X, pady=8)
                
                lbl_vec_title = tk.Label(
                    vector_frame, text="Estado del Vector Lineal (caminos):",
                    font=("Helvetica", 8, "bold"), bg="#f8f9fa", fg="#5f6368", anchor="w"
                )
                lbl_vec_title.pack(fill=tk.X, padx=8, pady=(4, 2))
                
                # Crear cajitas visuales para cada nodo en el vector lineal
                boxes_container = tk.Frame(vector_frame, bg="#f8f9fa")
                boxes_container.pack(fill=tk.X, padx=8, pady=(0, 6), anchor="w")
                
                # Solo mostrar los nodos ordenados
                for nid in sorted(vector_state.keys()):
                    state = vector_state[nid]
                    padre = state["padre"]
                    acum = state["acumulado"]
                    
                    # Formatear acumulado
                    if acum == float('inf') or acum == float('-inf'):
                        acum_s = "∞"
                    else:
                        acum_s = str(int(acum)) if acum.is_integer() else f"{acum:.1f}"
                        
                    padre_s = str(padre) if padre else "—"
                    
                    # Resaltar el nodo actual de este paso
                    is_current = (nid == node_id)
                    box_bg = "#e8f0fe" if is_current else "#ffffff"
                    box_outline = "#1a73e8" if is_current else "#dadce0"
                    
                    box = tk.Frame(boxes_container, bg=box_bg, bd=1, relief=tk.SOLID, highlightbackground=box_outline)
                    box.pack(side=tk.LEFT, padx=3)
                    
                    lbl_box_id = tk.Label(box, text=f"Nodo {nid}", font=("Helvetica", 8, "bold"), bg=box_bg, fg="#202124", padx=5)
                    lbl_box_id.pack()
                    
                    lbl_box_val = tk.Label(
                        box, text=f"Costo: {acum_s}\nPadre: {padre_s}", 
                        font=("Helvetica", 7), bg=box_bg, fg="#5f6368", padx=5, pady=2
                    )
                    lbl_box_val.pack()

        except Exception as e:
            messagebox.showerror("Error al Resolver", str(e))
