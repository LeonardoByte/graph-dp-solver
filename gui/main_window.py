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
        self.geometry("1200x650")
        self.minimum_width = 1100
        self.minimum_height = 600
        self.minsize(self.minimum_width, self.minimum_height)
        
        # Estado de navegación
        self.active_sidebar_button = None
        self.active_main_frame = None
        
        # Construir Interfaz
        self._init_ui()
        
        # Mostrar pantalla inicial (Ingreso por texto a la derecha, Canvas a la izquierda)
        self.show_ingreso_view()

    def _init_ui(self):
        # 1. Barra Lateral Izquierda (Sidebar)
        self.sidebar = tk.Frame(self, bg="#1e293b", width=160)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Logo o Título de la Aplicación en Sidebar
        app_title_frame = tk.Frame(self.sidebar, bg="#0f172a", height=60)
        app_title_frame.pack(fill=tk.X)
        app_title_frame.pack_propagate(False)
        
        app_title = tk.Label(
            app_title_frame, text="Graph DP Solver", 
            font=("Helvetica", 12, "bold"), fg="#f8fafc", bg="#0f172a"
        )
        app_title.pack(pady=15, padx=7)
        
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
        
        self.rb_min = tk.Radiobutton(
            opt_panel, text="Minimizar Costo", variable=self.opt_var, value="Min",
            bg="#0f172a", fg="#f8fafc", selectcolor="#0f172a",
            font=("Helvetica", 9), activebackground="#0f172a", activeforeground="#f8fafc",
            command=self.on_mode_changed, cursor="hand2"
        )
        self.rb_min.pack(fill=tk.X, pady=2)
        
        self.rb_max = tk.Radiobutton(
            opt_panel, text="Maximizar Ganancia", variable=self.opt_var, value="Max",
            bg="#0f172a", fg="#f8fafc", selectcolor="#0f172a",
            font=("Helvetica", 9), activebackground="#0f172a", activeforeground="#f8fafc",
            command=self.on_mode_changed, cursor="hand2"
        )
        self.rb_max.pack(fill=tk.X, pady=2)
        
        # 2. Área de Contenido Principal (Derecha)
        self.content_area = tk.Frame(self, bg="#ffffff")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- DIVISIÓN ESTRICTA 40-60 ---
        # Panel Izquierdo para el Canvas del Grafo (40% de ancho)
        self.left_panel = tk.Frame(self.content_area, bg="#ffffff")
        self.left_panel.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        
        # Panel Derecho para las vistas de Respuestas/Texto (60% de ancho)
        self.right_panel = tk.Frame(self.content_area, bg="#ffffff")
        self.right_panel.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)
        
        # Separador visual entre paneles
        self.separator = tk.Frame(self.content_area, bg="#dadce0", width=1)
        self.separator.place(relx=0.4, rely=0, relheight=1)
        
        # Inicializar e inyectar el CanvasPanel fijo en la izquierda
        self.canvas_panel = CanvasPanel(self.left_panel, self.controller)
        self.canvas_panel.pack(fill=tk.BOTH, expand=True)
        
        # Instanciar el TextPanel que compartirá estado y se sincronizará
        self.text_panel = TextPanel(self.right_panel, self.controller)

    def create_nav_button(self, name, command):
        btn_frame = tk.Frame(self.sidebar, bg="#1e293b", height=50)
        btn_frame.pack(fill=tk.X)
        btn_frame.pack_propagate(False)
        
        indicator = tk.Frame(btn_frame, bg="#1e293b", width=4) # Un pixel más delgado
        indicator.pack(side=tk.LEFT, fill=tk.Y)
        
        btn = tk.Button(
            btn_frame, text=name, command=command,
            font=("Helvetica", 9, "bold"), fg="#94a3b8", bg="#1e293b", # Fuente ligeramente reducida a 9
            relief=tk.FLAT, activebackground="#334155", activeforeground="#f8fafc",
            anchor="w", padx=8, cursor="hand2" # Padding reducido de 15 a 8 para que no se corte
        )
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.nav_buttons[name] = {"frame": btn_frame, "button": btn, "indicator": indicator}
        
        btn.bind("<Enter>", lambda e: self.on_btn_hover(name, True))
        btn.bind("<Leave>", lambda e: self.on_btn_hover(name, False))

    def on_btn_hover(self, name, is_hover):
        if self.active_sidebar_button != name:
            bg_color = "#334155" if is_hover else "#1e293b"
            fg_color = "#cbd5e1" if is_hover else "#94a3b8"
            self.nav_buttons[name]["button"].config(bg=bg_color, fg=fg_color)
            self.nav_buttons[name]["frame"].config(bg=bg_color)

    def set_active_sidebar_button(self, name):
        if self.active_sidebar_button:
            prev = self.active_sidebar_button
            self.nav_buttons[prev]["button"].config(bg="#1e293b", fg="#94a3b8")
            self.nav_buttons[prev]["frame"].config(bg="#1e293b")
            self.nav_buttons[prev]["indicator"].config(bg="#1e293b")
            
        self.active_sidebar_button = name
        self.nav_buttons[name]["button"].config(bg="#334155", fg="#f8fafc")
        self.nav_buttons[name]["frame"].config(bg="#334155")
        self.nav_buttons[name]["indicator"].config(bg="#3b82f6")

    def switch_right_frame(self, frame_instance_or_class, *args, **kwargs):
        """Monta un panel en el contenedor derecho (60%)."""
        if self.active_main_frame:
            self.active_main_frame.pack_forget()
            # Si era una instancia creada al vuelo (no text_panel compartido), la destruimos
            if self.active_main_frame != self.text_panel:
                self.active_main_frame.destroy()
            
        if isinstance(frame_instance_or_class, tk.Frame):
            self.active_main_frame = frame_instance_or_class
        else:
            self.active_main_frame = frame_instance_or_class(self.right_panel, self.controller, *args, **kwargs)
            
        self.active_main_frame.pack(fill=tk.BOTH, expand=True)
        return self.active_main_frame

    def on_mode_changed(self):
        self.controller.set_mode(self.opt_var.get())
        self.canvas_panel.set_highlighted_path([])

    def on_graph_modified(self):
        """
        Callback invocado cada vez que se realizan cambios sobre el grafo
        (dibujando nodos, aristas o al validar en el panel de texto).
        """
        self.canvas_panel.redraw()
        # Si la vista activa a la derecha es el editor de texto, sincronizar el texto
        if self.active_main_frame == self.text_panel:
            self.text_panel.update_text_from_graph()

    # --- CONTROL DE VISTAS (Navegación en panel derecho) ---

    def show_ingreso_view(self):
        self.set_active_sidebar_button("Ingreso")
        # Mostrar el TextPanel compartido a la derecha
        self.switch_right_frame(self.text_panel)
        # Sincronizar el texto con el grafo actual
        self.text_panel.update_text_from_graph()
        self.canvas_panel.redraw()

    def show_historial_view(self):
        self.set_active_sidebar_button("Historial")
        
        # Al cargar un grafo del historial, actualizamos el canvas y el texto
        def on_load_callback():
            self.canvas_panel.redraw()
            self.text_panel.update_text_from_graph()
            
        history_view = self.switch_right_frame(HistoryPanel)
        history_view.on_graph_modified = on_load_callback

    def show_regressive_view(self):
        if not self.controller.graph.nodes:
            messagebox.showwarning("Grafo Vacío", "Por favor, dibuje o ingrese un grafo antes de resolver.")
            self.show_ingreso_view()
            return
            
        self.set_active_sidebar_button("Resolución Regresiva")
        # El panel del canvas se pasa para poder resaltar la ruta óptima
        self.switch_right_frame(RegressivePanel, self.canvas_panel)

    def show_progressive_view(self):
        if not self.controller.graph.nodes:
            messagebox.showwarning("Grafo Vacío", "Por favor, dibuje o ingrese un grafo antes de resolver.")
            self.show_ingreso_view()
            return
            
        self.set_active_sidebar_button("Resolución Progresiva")
        self.switch_right_frame(ProgressivePanel, self.canvas_panel)
