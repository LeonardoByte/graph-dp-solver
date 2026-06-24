import os
from controllers.graph_controller import GraphController
from gui.main_window import MainWindow

def main():
    # Crear el directorio del historial si no existe
    history_dir = "historial_grafos"
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    # Inicializar el controlador
    controller = GraphController()

    # Inicializar la ventana principal
    app = MainWindow(controller)
    
    # Iniciar la aplicación
    app.mainloop()

if __name__ == "__main__":
    main()
