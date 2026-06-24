import tkinter as tk
from tkinter import messagebox
from gui.canvas_panel import CanvasPanel
from gui.text_panel import TextPanel
from gui.history_panel import HistoryPanel
from gui.resolution_panels import RegressivePanel, ProgressivePanel

class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Configuración básica de la ventana
        self.title("Resolutor de Programación Dinámica en Grafos")
        self.geometry("1150x650")
        self.minimum_width = 1000
        self.minimum_height = 600
        self.minsize(self.minimum_width, self.minimum_height)
        
        # Estado de navegación
        self.active_sidebar_button = None
        self.active_main_frame = None
        
        # Inicializar vistas compartidas
        self._init_shared_views()
        
        # Construir Interfaz
        self._init_ui()
        
        # Mostrar pantalla inicial (Ingreso)
        self.show_ingreso_view()

    def _init_shared_views(self):
        # El Canvas y TextPanel se instancian una sola vez para mantener el estado del grafo
        # Creamos un contenedor temporal fuera de la vista principal
        self.canvas_panel = CanvasPanel(self, self.controller)
        self.text_panel = TextPanel(self, self.controller)

    def _init_ui(self):
        # 1. Barra Lateral Izquierda (Sidebar)
        self.sidebar = tk.Frame(self, bg="#1e293b", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Logo o Título de la Aplicación en Sidebar
        app_title_frame = tk.Frame(self.sidebar, bg="#0f172a", height=60)
        app_title_frame.pack(fill=tk.X)
        app_title_frame.pack_propagate(False)
        
        app_title = tk.Label(
            app_title_frame, text="Graph DP Solver", 
            font=("Helvetica", 14, "bold"), fg="#f8fafc", bg="#0f172a"
        )
        app_title.pack(pady=15, padx=10)
        
        # Botones de navegación lateral
        self.nav_buttons = {}
        
        self.create_nav_button("Ingreso", self.show_ingreso_view)
        self.create_nav_button("Historial", self.show_historial_view)
        self.create_nav_button("Resolución Regresiva", self.show_regressive_view)
        self.create_nav_button("Resolución Progresiva", self.show_progressive_view)
        
        # Separador / Relleno
        filler = tk.Frame(self.sidebar, bg="#1e293b")
        filler.pack(fill=tk.BOTH, expand=True)
        
        # Panel del selector de optimización en la parte inferior de la barra lateral
        opt_panel = tk.Frame(self.sidebar, bg="#0f172a", pady=15, padx=15)
        opt_panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        opt_title = tk.Label(
            opt_panel, text="OBJETIVO", 
            font=("Helvetica", 9, "bold"), fg="#94a3b8", bg="#0f172a", anchor="w"
        )
        opt_title.pack(fill=tk.X, pady=(0, 8))
        
        self.opt_var = tk.StringVar(value="Min")
        
        # Botón de opción Minimizar
        self.rb_min = tk.Radiobutton(
            opt_panel, text="Minimizar Costo", variable=self.opt_var, value="Min",
            bg="#0f172a", fg="#f8fafc", selectcolor="#0f172a",
            font=("Helvetica", 9), activebackground="#0f172a", activeforeground="#f8fafc",
            command=self.on_mode_changed, cursor="hand2"
        )
        self.rb_min.pack(fill=tk.X, pady=2)
        
        # Botón de opción Maximizar
        self.rb_max = tk.Radiobutton(
            opt_panel, text="Maximizar Ganancia", variable=self.opt_var, value="Max",
            bg="#0f172a", fg="#f8fafc", selectcolor="#0f172a",
            font=("Helvetica", 9), activebackground="#0f172a", activeforeground="#f8fafc",
            command=self.on_mode_changed, cursor="hand2"
        )
        self.rb_max.pack(fill=tk.X, pady=2)
        
        # 2. Panel Central de Contenido
        self.content_area = tk.Frame(self, bg="#ffffff")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_nav_button(self, name, command):
        # Cada botón tiene una barrita indicadora de selección al lado
        btn_frame = tk.Frame(self.sidebar, bg="#1e293b", height=50)
        btn_frame.pack(fill=tk.X)
        btn_frame.pack_propagate(False)
        
        indicator = tk.Frame(btn_frame, bg="#1e293b", width=5)
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        btn = tk.Button(
            btn_frame, text=name, command=command,
            font=("Helvetica", 10, "bold"), fg="#94a3b8", bg="#1e293b",
            relief=tk.FLAT, activebackground="#334155", activeforeground="#f8fafc",
            anchor="w", padx=15, cursor="hand2"
        )
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Guardar referencias para efectos visuales de hover y active
        self.nav_buttons[name] = {"frame": btn_frame, "button": btn, "indicator": indicator}
        
        # Bindeos de hover
        btn.bind("<Enter>", lambda e: self.on_btn_hover(name, True))
        btn.bind("<Leave>", lambda e: self.on_btn_hover(name, False))

    def on_btn_hover(self, name, is_hover):
        # Solo aplicar hover si el botón no es el activo
        if self.active_sidebar_button != name:
            bg_color = "#334155" if is_hover else "#1e293b"
            fg_color = "#cbd5e1" if is_hover else "#94a3b8"
            self.nav_buttons[name]["button"].config(bg=bg_color, fg=fg_color)
            self.nav_buttons[name]["frame"].config(bg=bg_color)

    def set_active_sidebar_button(self, name):
        # Desactivar botón activo anterior
        if self.active_sidebar_button:
            prev = self.active_sidebar_button
            self.nav_buttons[prev]["button"].config(bg="#1e293b", fg="#94a3b8")
            self.nav_buttons[prev]["frame"].config(bg="#1e293b")
            self.nav_buttons[prev]["indicator"].config(bg="#1e293b")
            
        # Activar el nuevo
        self.active_sidebar_button = name
        self.nav_buttons[name]["button"].config(bg="#334155", fg="#f8fafc")
        self.nav_buttons[name]["frame"].config(bg="#334155")
        self.nav_buttons[name]["indicator"].config(bg="#3b82f6")  # Azul brillante

    def switch_main_frame(self, new_frame_class, *args, **kwargs):
        """Reemplaza el panel de contenido central por una nueva instancia de vista."""
        if self.active_main_frame:
            self.active_main_frame.pack_forget()
            self.active_main_frame.destroy()
            
        self.active_main_frame = new_frame_class(self.content_area, self.controller, *args, **kwargs)
        self.active_main_frame.pack(fill=tk.BOTH, expand=True)
        return self.active_main_frame

    def on_mode_changed(self):
        # Sincronizar el modo de optimización en el controlador
        self.controller.set_mode(self.opt_var.get())
        # Borrar camino resaltado en el canvas si cambia el modo
        self.canvas_panel.set_highlighted_path([])

    # --- CONTROL DE VISTAS (Navegación) ---

    def show_ingreso_view(self):
        self.set_active_sidebar_button("Ingreso")
        
        # Creamos un panel de ingreso contenedor especial
        if self.active_main_frame:
            self.active_main_frame.pack_forget()
            self.active_main_frame.destroy()
            
        ingreso_frame = tk.Frame(self.content_area, bg="#ffffff")
        ingreso_frame.pack(fill=tk.BOTH, expand=True)
        self.active_main_frame = ingreso_frame
        
        # Barra superior con los 2 botones alternantes
        top_bar = tk.Frame(ingreso_frame, bg="#f5f6f8", height=50)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Frame del contenido intercambiable del ingreso (visual vs texto)
        ingreso_content = tk.Frame(ingreso_frame, bg="#ffffff")
        ingreso_content.pack(fill=tk.BOTH, expand=True)
        
        # Mantener referencia de los sub-paneles y montarlos
        # Los panels ya están instanciados en self.canvas_panel y self.text_panel
        # para no perder el estado.
        
        active_sub_panel = [None]  # Contenedor mutable
        
        def show_sub_panel(mode):
            # Limpiar panel actual
            if active_sub_panel[0]:
                active_sub_panel[0].pack_forget()
                
            if mode == "visual":
                btn_visual.config(bg="#1a73e8", fg="#ffffff")
                btn_texto.config(bg="#f1f3f4", fg="#3c4043")
                
                # Desmontar text_panel de su padre anterior si lo tenía y asociarlo a este contenedor
                self.canvas_panel.pack_forget()
                self.canvas_panel.master = ingreso_content
                self.canvas_panel.pack(fill=tk.BOTH, expand=True)
                active_sub_panel[0] = self.canvas_panel
                self.canvas_panel.redraw()
            else:  # texto
                btn_texto.config(bg="#1a73e8", fg="#ffffff")
                btn_visual.config(bg="#f1f3f4", fg="#3c4043")
                
                # Sincronizar el texto plano antes de mostrarlo
                self.text_panel.update_text_from_graph()
                
                self.text_panel.pack_forget()
                self.text_panel.master = ingreso_content
                self.text_panel.pack(fill=tk.BOTH, expand=True)
                active_sub_panel[0] = self.text_panel
                
        # Botón Ingreso Visual
        btn_visual = tk.Button(
            top_bar, text="Ingreso Visual (Canvas)", 
            command=lambda: show_sub_panel("visual"),
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, cursor="hand2",
            padx=15, pady=5
        )
        btn_visual.pack(side=tk.LEFT, padx=(15, 5), pady=10)
        
        # Botón Ingreso Texto
        btn_texto = tk.Button(
            top_bar, text="Ingreso Texto Plano", 
            command=lambda: show_sub_panel("texto"),
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, cursor="hand2",
            padx=15, pady=5
        )
        btn_texto.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Inicializar en visual
        show_sub_panel("visual")
        
        # Añadir callback al contenedor de ingreso para actualizaciones mutuas
        def on_graph_modified():
            # Cuando el canvas se modifica, actualiza la caja de texto en segundo plano
            self.text_panel.update_text_from_graph()
            
        ingreso_frame.on_graph_modified = on_graph_modified

    def show_historial_view(self):
        self.set_active_sidebar_button("Historial")
        
        # Callback para cuando se cargue un grafo del historial, redibujar el canvas
        def on_graph_modified():
            self.canvas_panel.redraw()
            self.text_panel.update_text_from_graph()
            
        history_view = self.switch_main_frame(HistoryPanel)
        history_view.on_graph_modified = on_graph_modified

    def show_regressive_view(self):
        if not self.controller.graph.nodes:
            messagebox.showwarning("Grafo Vacío", "Por favor, dibuje o ingrese un grafo antes de resolver.")
            self.show_ingreso_view()
            return
            
        self.set_active_sidebar_button("Resolución Regresiva")
        # Pasamos el panel de canvas como referencia para poder iluminar la ruta
        self.switch_main_frame(RegressivePanel, self.canvas_panel)

    def show_progressive_view(self):
        if not self.controller.graph.nodes:
            messagebox.showwarning("Grafo Vacío", "Por favor, dibuje o ingrese un grafo antes de resolver.")
            self.show_ingreso_view()
            return
            
        self.set_active_sidebar_button("Resolución Progresiva")
        self.switch_main_frame(ProgressivePanel, self.canvas_panel)
