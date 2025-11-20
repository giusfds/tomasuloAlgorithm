"""
Ponto de entrada principal do simulador de Tomasulo
"""
import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import SimulatorGUI


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    # Criar e mostrar janela principal
    window = SimulatorGUI()
    window.show()
    
    # Executar aplicação
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
