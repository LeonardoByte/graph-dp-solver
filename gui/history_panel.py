import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

class HistoryPanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        
        self._init_ui()
        self.refresh_history()

    def _init_ui(self):
        # Título superior
        self.title_label = tk.Label(
            self, 
            text="Historial de Grafos Guardados",
            bg="#ffffff", fg="#202124", 
            font=("Helvetica", 14, "bold"), pady=15
        )
        self.title_label.pack(fill=tk.X, padx=15)
        
        # Contenedor para la tabla de historial y scrollbar
        table_frame = tk.Frame(self, bg="#ffffff")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.scrollbar = tk.Scrollbar(table_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para mostrar la lista de archivos de forma elegante
        self.tree = ttk.Treeview(
            table_frame, 
            columns=("Archivo",), 
            show="headings", 
            yscrollcommand=self.scrollbar.set,
            selectmode="browse"
        )
        self.tree.heading("Archivo", text="Nombre del Grafo (.txt)")
        self.tree.column("Archivo", anchor=tk.W, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.tree.yview)
        
        # Panel de botones
        buttons_frame = tk.Frame(self, bg="#ffffff")
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Botón Guardar Grafo Actual
        self.btn_save = tk.Button(
            buttons_frame, 
            text="Guardar Grafo Actual", 
            command=self.save_current_graph,
            bg="#34a853", fg="#ffffff", relief=tk.FLAT,
            font=("Helvetica", 9, "bold"), cursor="hand2",
            activebackground="#2d8e47", activeforeground="#ffffff",
            padx=10, pady=8
        )
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botón Cargar Grafo Seleccionado
        self.btn_load = tk.Button(
            buttons_frame, 
            text="Cargar Grafo", 
            command=self.load_selected_graph,
            bg="#1a73e8", fg="#ffffff", relief=tk.FLAT,
            font=("Helvetica", 9, "bold"), cursor="hand2",
            activebackground="#1557b0", activeforeground="#ffffff",
            padx=10, pady=8
        )
        self.btn_load.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botón Eliminar Grafo
        self.btn_delete = tk.Button(
            buttons_frame, 
            text="Eliminar Grafo", 
            command=self.delete_selected_graph,
            bg="#ea4335", fg="#ffffff", relief=tk.FLAT,
            font=("Helvetica", 9, "bold"), cursor="hand2",
            activebackground="#d93025", activeforeground="#ffffff",
            padx=10, pady=8
        )
        self.btn_delete.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Configurar estilos de la tabla ttk
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    def refresh_history(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Leer archivos del historial
        try:
            files = self.controller.get_history_list()
            for file in files:
                self.tree.insert("", tk.END, values=(file,))
        except Exception as e:
            messagebox.showerror("Error al leer historial", str(e))

    def save_current_graph(self):
        if not self.controller.graph.nodes:
            messagebox.showwarning("Grafo Vacío", "No hay nodos en el grafo actual para guardar.")
            return
            
        # Abrir ventana de diálogo para ingresar el nombre
        name = simpledialog.askstring(
            "Guardar Grafo", 
            "Ingrese el nombre para este grafo (se guardará con la fecha/hora):",
            parent=self
        )
        
        if name is not None:
            # Si no ingresó nada, se auto-generará
            try:
                filename = self.controller.save_to_history(name)
                self.refresh_history()
                messagebox.showinfo("Grafo Guardado", f"Grafo guardado exitosamente como:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error al Guardar", str(e))

    def load_selected_graph(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selección vacía", "Por favor, seleccione un grafo del historial para cargar.")
            return
            
        item = selected_items[0]
        filename = self.tree.item(item, "values")[0]
        
        try:
            self.controller.load_from_history(filename)
            
            # Notificar para redibujar el canvas
            if hasattr(self.master, "on_graph_modified"):
                self.master.on_graph_modified()
                
            messagebox.showinfo("Cargado con Éxito", f"El grafo '{filename}' se ha cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error al Cargar", str(e))

    def delete_selected_graph(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selección vacía", "Por favor, seleccione un grafo del historial para eliminar.")
            return
            
        item = selected_items[0]
        filename = self.tree.item(item, "values")[0]
        
        ans = messagebox.askyesno(
            "Eliminar Grafo", 
            f"¿Está seguro de que desea eliminar el archivo '{filename}' permanentemente?"
        )
        
        if ans:
            try:
                self.controller.delete_from_history(filename)
                self.refresh_history()
                messagebox.showinfo("Eliminado", f"El archivo '{filename}' ha sido eliminado.")
            except Exception as e:
                messagebox.showerror("Error al eliminar", str(e))
