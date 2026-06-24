import tkinter as tk
from tkinter import messagebox

class TextPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        
        self._init_ui()

    def _init_ui(self):
        # Etiqueta de instrucciones superior
        self.header_label = tk.Label(
            self, 
            text="Ingrese la definición del grafo línea por línea con el formato:\n"
                 "[Nodo_Origen] [Nodo_Destino] [Peso_Arista]\n\n"
                 "Ejemplo:\n"
                 "1 2 4\n1 3 3\n2 4 7\n3 4 2",
            justify=tk.LEFT, bg="#ffffff", fg="#5f6368", 
            font=("Helvetica", 10), pady=10
        )
        self.header_label.pack(fill=tk.X, padx=15)
        
        # Frame del editor con Scrollbar
        editor_frame = tk.Frame(self, bg="#ffffff")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.scrollbar = tk.Scrollbar(editor_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_widget = tk.Text(
            editor_frame, 
            yscrollcommand=self.scrollbar.set,
            font=("Consolas", 11), 
            bd=1, relief=tk.SOLID, 
            highlightthickness=1, highlightbackground="#dadce0"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text_widget.yview)
        
        # Botón para Cargar/Validar el Grafo
        self.btn_load = tk.Button(
            self, 
            text="Validar y Cargar Grafo", 
            command=self.validate_and_load,
            bg="#1a73e8", fg="#ffffff", relief=tk.FLAT,
            font=("Helvetica", 10, "bold"), cursor="hand2",
            activebackground="#1557b0", activeforeground="#ffffff",
            pady=8
        )
        self.btn_load.pack(fill=tk.X, padx=15, pady=15)

    def validate_and_load(self):
        text_content = self.text_widget.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("Advertencia", "El área de texto está vacía.")
            return
            
        try:
            # Procesar el grafo
            self.controller.load_from_text(text_content)
            
            # Sincronizar y redibujar el canvas
            if hasattr(self.master, "on_graph_modified"):
                self.master.on_graph_modified()
                
            messagebox.showinfo("Grafo Cargado", "¡El grafo se ha validado y cargado correctamente en el canvas!")
        except Exception as e:
            messagebox.showerror("Error de Validación", str(e))

    def update_text_from_graph(self):
        """
        Lee el grafo del controlador y escribe su representación en texto
        en el widget de texto (utilizado para mantener sincronizado el texto con el canvas).
        """
        text_repr = self.controller.get_text_representation()
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text_repr)
