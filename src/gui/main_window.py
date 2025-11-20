"""
Interface gráfica para o simulador de Tomasulo
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel, QTableWidget, 
    QTableWidgetItem, QSplitter, QGroupBox, QFileDialog,
    QMessageBox, QSpinBox, QFormLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from src.core.simulator import TomasuloSimulator
from src.mips.parser import MIPSParser


class SimulatorGUI(QMainWindow):
    """Interface gráfica principal do simulador"""
    
    def __init__(self):
        super().__init__()
        self.simulator = None
        self.parser = MIPSParser()
        self.auto_run_timer = QTimer()
        self.auto_run_timer.timeout.connect(self.step_simulation)
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle('Simulador de Tomasulo - Educacional')
        self.setGeometry(100, 100, 1600, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Splitter horizontal principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Painel esquerdo - Editor de código
        left_panel = self.create_code_panel()
        main_splitter.addWidget(left_panel)
        
        # Painel direito - Visualização
        right_panel = self.create_visualization_panel()
        main_splitter.addWidget(right_panel)
        
        # Proporções dos painéis
        main_splitter.setSizes([500, 1100])
        
        # Barra de status
        self.statusBar().showMessage('Pronto')
        
    def create_code_panel(self):
        """Cria o painel de código"""
        panel = QGroupBox("Código MIPS")
        layout = QVBoxLayout()
        
        # Editor de código
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont('Courier New', 10))
        self.code_editor.setPlaceholderText(
            "# Digite seu código MIPS aqui\n"
            "# Exemplo:\n"
            "ADDI R1, R0, 10\n"
            "ADDI R2, R0, 20\n"
            "ADD R3, R1, R2\n"
        )
        layout.addWidget(self.code_editor)
        
        # Botões de arquivo
        file_buttons_layout = QHBoxLayout()
        
        load_btn = QPushButton('Carregar Arquivo')
        load_btn.clicked.connect(self.load_file)
        file_buttons_layout.addWidget(load_btn)
        
        save_btn = QPushButton('Salvar Arquivo')
        save_btn.clicked.connect(self.save_file)
        file_buttons_layout.addWidget(save_btn)
        
        load_example_btn = QPushButton('Carregar Exemplo')
        load_example_btn.clicked.connect(self.load_example)
        file_buttons_layout.addWidget(load_example_btn)
        
        layout.addLayout(file_buttons_layout)
        
        # Configuração do simulador
        config_group = QGroupBox("Configuração")
        config_layout = QFormLayout()
        
        self.add_rs_spin = QSpinBox()
        self.add_rs_spin.setRange(1, 10)
        self.add_rs_spin.setValue(3)
        config_layout.addRow("Add RS:", self.add_rs_spin)
        
        self.mul_rs_spin = QSpinBox()
        self.mul_rs_spin.setRange(1, 10)
        self.mul_rs_spin.setValue(2)
        config_layout.addRow("Mult RS:", self.mul_rs_spin)
        
        self.rob_size_spin = QSpinBox()
        self.rob_size_spin.setRange(4, 32)
        self.rob_size_spin.setValue(16)
        config_layout.addRow("ROB Size:", self.rob_size_spin)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Botões de controle
        control_layout = QVBoxLayout()
        
        self.load_btn = QPushButton('Carregar Programa')
        self.load_btn.clicked.connect(self.load_program)
        control_layout.addWidget(self.load_btn)
        
        self.step_btn = QPushButton('Próximo Ciclo')
        self.step_btn.clicked.connect(self.step_simulation)
        self.step_btn.setEnabled(False)
        control_layout.addWidget(self.step_btn)
        
        self.run_btn = QPushButton('Executar Tudo')
        self.run_btn.clicked.connect(self.run_simulation)
        self.run_btn.setEnabled(False)
        control_layout.addWidget(self.run_btn)
        
        self.auto_run_btn = QPushButton('Execução Automática')
        self.auto_run_btn.clicked.connect(self.toggle_auto_run)
        self.auto_run_btn.setEnabled(False)
        control_layout.addWidget(self.auto_run_btn)
        
        self.reset_btn = QPushButton('Resetar')
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.reset_btn.setEnabled(False)
        control_layout.addWidget(self.reset_btn)
        
        layout.addLayout(control_layout)
        
        panel.setLayout(layout)
        return panel
        
    def create_visualization_panel(self):
        """Cria o painel de visualização"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Informações de ciclo e status
        info_layout = QHBoxLayout()
        
        self.cycle_label = QLabel('Ciclo: 0')
        self.cycle_label.setFont(QFont('Arial', 12, QFont.Bold))
        info_layout.addWidget(self.cycle_label)
        
        self.pc_label = QLabel('PC: 0')
        self.pc_label.setFont(QFont('Arial', 12, QFont.Bold))
        info_layout.addWidget(self.pc_label)
        
        self.status_label = QLabel('Status: Aguardando')
        self.status_label.setFont(QFont('Arial', 12, QFont.Bold))
        info_layout.addWidget(self.status_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Splitter vertical para tabelas
        tables_splitter = QSplitter(Qt.Vertical)
        
        # Tabela de instruções
        inst_group = QGroupBox("Instruções")
        inst_layout = QVBoxLayout()
        self.instructions_table = QTableWidget()
        self.instructions_table.setColumnCount(8)
        self.instructions_table.setHorizontalHeaderLabels([
            'PC', 'Instrução', 'Estágio', 'Issue', 'Exec', 
            'Write', 'Commit', 'ROB'
        ])
        inst_layout.addWidget(self.instructions_table)
        inst_group.setLayout(inst_layout)
        tables_splitter.addWidget(inst_group)
        
        # Tabela de Reservation Stations
        rs_group = QGroupBox("Reservation Stations")
        rs_layout = QVBoxLayout()
        self.rs_table = QTableWidget()
        self.rs_table.setColumnCount(8)
        self.rs_table.setHorizontalHeaderLabels([
            'Nome', 'Busy', 'Op', 'Vj', 'Vk', 'Qj', 'Qk', 'Dest'
        ])
        rs_layout.addWidget(self.rs_table)
        rs_group.setLayout(rs_layout)
        tables_splitter.addWidget(rs_group)
        
        # Tabela de ROB
        rob_group = QGroupBox("Reorder Buffer (ROB)")
        rob_layout = QVBoxLayout()
        self.rob_table = QTableWidget()
        self.rob_table.setColumnCount(7)
        self.rob_table.setHorizontalHeaderLabels([
            'Entry', 'Busy', 'Instrução', 'Estado', 'Destino', 'Valor', 'Ready'
        ])
        rob_layout.addWidget(self.rob_table)
        rob_group.setLayout(rob_layout)
        tables_splitter.addWidget(rob_group)
        
        # Registradores e Métricas
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Tabela de registradores
        reg_group = QGroupBox("Registradores")
        reg_layout = QVBoxLayout()
        self.registers_table = QTableWidget()
        self.registers_table.setColumnCount(4)
        self.registers_table.setHorizontalHeaderLabels(['Reg', 'Valor', 'Reg', 'Valor'])
        reg_layout.addWidget(self.registers_table)
        reg_group.setLayout(reg_layout)
        bottom_splitter.addWidget(reg_group)
        
        # Métricas de desempenho
        metrics_group = QGroupBox("Métricas de Desempenho")
        metrics_layout = QVBoxLayout()
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(200)
        metrics_layout.addWidget(self.metrics_text)
        metrics_group.setLayout(metrics_layout)
        bottom_splitter.addWidget(metrics_group)
        
        tables_splitter.addWidget(bottom_splitter)
        
        layout.addWidget(tables_splitter)
        
        panel.setLayout(layout)
        return panel
        
    def load_file(self):
        """Carrega um arquivo MIPS"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Abrir arquivo MIPS', '', 'MIPS Files (*.asm *.mips);;All Files (*)'
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.code_editor.setPlainText(f.read())
                self.statusBar().showMessage(f'Arquivo carregado: {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao carregar arquivo: {str(e)}')
                
    def save_file(self):
        """Salva o código em um arquivo"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Salvar arquivo MIPS', '', 'MIPS Files (*.asm);;All Files (*)'
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.code_editor.toPlainText())
                self.statusBar().showMessage(f'Arquivo salvo: {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao salvar arquivo: {str(e)}')
                
    def load_example(self):
        """Carrega um programa de exemplo"""
        example = """# Programa de exemplo - Cálculo de soma
# Demonstra hazards de dados e execução fora de ordem

ADDI R1, R0, 10    # R1 = 10
ADDI R2, R0, 20    # R2 = 20
ADD R3, R1, R2     # R3 = R1 + R2 = 30
SUB R4, R3, R1     # R4 = R3 - R1 = 20
MUL R5, R3, R2     # R5 = R3 * R2 = 600
ADDI R6, R0, 2     # R6 = 2
DIV R7, R5, R6     # R7 = R5 / R6 = 300
"""
        self.code_editor.setPlainText(example)
        self.statusBar().showMessage('Exemplo carregado')
        
    def load_program(self):
        """Carrega o programa no simulador"""
        code = self.code_editor.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, 'Aviso', 'Por favor, digite um programa MIPS')
            return
            
        try:
            # Parse do programa
            self.parser = MIPSParser()
            instructions = self.parser.parse_program(code)
            
            if not instructions:
                QMessageBox.warning(self, 'Aviso', 'Nenhuma instrução válida encontrada')
                return
                
            # Criar simulador com configuração
            config = {
                'add_rs': self.add_rs_spin.value(),
                'mul_rs': self.mul_rs_spin.value(),
                'rob_size': self.rob_size_spin.value(),
            }
            
            self.simulator = TomasuloSimulator(config)
            self.simulator.load_program(instructions)
            
            # Atualizar interface
            self.update_display()
            
            # Habilitar botões
            self.step_btn.setEnabled(True)
            self.run_btn.setEnabled(True)
            self.auto_run_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            
            self.statusBar().showMessage(f'{len(instructions)} instruções carregadas')
            
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao carregar programa: {str(e)}')
            import traceback
            traceback.print_exc()
            
    def step_simulation(self):
        """Executa um ciclo da simulação"""
        if not self.simulator:
            return
            
        if not self.simulator.finished:
            self.simulator.step()
            self.update_display()
            
            if self.simulator.finished:
                self.auto_run_timer.stop()
                self.auto_run_btn.setText('Execução Automática')
                QMessageBox.information(self, 'Concluído', 'Simulação finalizada!')
                self.show_final_metrics()
        else:
            self.auto_run_timer.stop()
            self.auto_run_btn.setText('Execução Automática')
            
    def run_simulation(self):
        """Executa a simulação até o final"""
        if not self.simulator:
            return
            
        self.simulator.run_until_complete()
        self.update_display()
        self.show_final_metrics()
        
    def toggle_auto_run(self):
        """Alterna execução automática"""
        if self.auto_run_timer.isActive():
            self.auto_run_timer.stop()
            self.auto_run_btn.setText('Execução Automática')
        else:
            self.auto_run_timer.start(500)  # 500ms por ciclo
            self.auto_run_btn.setText('Pausar')
            
    def reset_simulation(self):
        """Reseta a simulação"""
        if self.simulator:
            self.simulator.reset()
            self.update_display()
            self.statusBar().showMessage('Simulação resetada')
            
    def show_final_metrics(self):
        """Mostra métricas finais"""
        if not self.simulator:
            return
            
        metrics = self.simulator.metrics
        bp = self.simulator.branch_predictor
        
        msg = f"""Simulação Finalizada!

Métricas de Desempenho:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total de Ciclos: {metrics.total_cycles}
Instruções Completadas: {metrics.instructions_completed}
IPC (Instructions Per Cycle): {metrics.get_ipc():.3f}

Ciclos de Bolha: {metrics.bubble_cycles}
Ciclos de Stall: {metrics.stall_cycles}

Desvios:
  Mispredictions: {metrics.branch_mispredictions}
  Predições: {bp.predictions}
  Taxa de Acerto: {bp.get_accuracy()*100:.1f}%
"""
        QMessageBox.information(self, 'Métricas Finais', msg)
        
    def update_display(self):
        """Atualiza toda a interface"""
        if not self.simulator:
            return
            
        # Atualizar labels
        self.cycle_label.setText(f'Ciclo: {self.simulator.current_cycle}')
        self.pc_label.setText(f'PC: {self.simulator.pc}')
        status = 'Finalizado' if self.simulator.finished else 'Executando'
        self.status_label.setText(f'Status: {status}')
        
        # Atualizar tabelas
        self.update_instructions_table()
        self.update_rs_table()
        self.update_rob_table()
        self.update_registers_table()
        self.update_metrics()
        
    def update_instructions_table(self):
        """Atualiza a tabela de instruções"""
        instructions = self.simulator.instructions
        self.instructions_table.setRowCount(len(instructions))
        
        for i, inst in enumerate(instructions):
            self.instructions_table.setItem(i, 0, QTableWidgetItem(str(inst.pc)))
            self.instructions_table.setItem(i, 1, QTableWidgetItem(str(inst)))
            self.instructions_table.setItem(i, 2, QTableWidgetItem(inst.stage.value))
            self.instructions_table.setItem(i, 3, QTableWidgetItem(
                str(inst.issue_cycle) if inst.issue_cycle else '-'
            ))
            self.instructions_table.setItem(i, 4, QTableWidgetItem(
                str(inst.exec_start_cycle) if inst.exec_start_cycle else '-'
            ))
            self.instructions_table.setItem(i, 5, QTableWidgetItem(
                str(inst.write_cycle) if inst.write_cycle else '-'
            ))
            self.instructions_table.setItem(i, 6, QTableWidgetItem(
                str(inst.commit_cycle) if inst.commit_cycle else '-'
            ))
            self.instructions_table.setItem(i, 7, QTableWidgetItem(
                f'ROB{inst.rob_entry}' if inst.rob_entry is not None else '-'
            ))
            
            # Colorir linha baseado no estágio
            color = self._get_stage_color(inst.stage)
            for j in range(8):
                item = self.instructions_table.item(i, j)
                if item:
                    item.setBackground(color)
                    
        self.instructions_table.resizeColumnsToContents()
        
    def update_rs_table(self):
        """Atualiza a tabela de reservation stations"""
        all_rs = (self.simulator.add_rs + self.simulator.mul_rs + 
                  self.simulator.load_rs + self.simulator.store_rs)
        
        self.rs_table.setRowCount(len(all_rs))
        
        for i, rs in enumerate(all_rs):
            self.rs_table.setItem(i, 0, QTableWidgetItem(rs.name))
            self.rs_table.setItem(i, 1, QTableWidgetItem('Sim' if rs.busy else 'Não'))
            self.rs_table.setItem(i, 2, QTableWidgetItem(
                rs.op.value if rs.op else '-'
            ))
            self.rs_table.setItem(i, 3, QTableWidgetItem(
                str(rs.vj) if rs.vj is not None else '-'
            ))
            self.rs_table.setItem(i, 4, QTableWidgetItem(
                str(rs.vk) if rs.vk is not None else '-'
            ))
            self.rs_table.setItem(i, 5, QTableWidgetItem(
                f'ROB{rs.qj}' if rs.qj is not None else '-'
            ))
            self.rs_table.setItem(i, 6, QTableWidgetItem(
                f'ROB{rs.qk}' if rs.qk is not None else '-'
            ))
            self.rs_table.setItem(i, 7, QTableWidgetItem(
                f'ROB{rs.dest}' if rs.dest is not None else '-'
            ))
            
            # Colorir se ocupado
            color = QColor(255, 200, 200) if rs.busy else QColor(200, 255, 200)
            for j in range(8):
                item = self.rs_table.item(i, j)
                if item:
                    item.setBackground(color)
                    
        self.rs_table.resizeColumnsToContents()
        
    def update_rob_table(self):
        """Atualiza a tabela do ROB"""
        self.rob_table.setRowCount(len(self.simulator.rob))
        
        for i, entry in enumerate(self.simulator.rob):
            # Marcar head e tail
            entry_text = f'ROB{i}'
            if i == self.simulator.rob_head:
                entry_text += ' (H)'
            if i == self.simulator.rob_tail:
                entry_text += ' (T)'
                
            self.rob_table.setItem(i, 0, QTableWidgetItem(entry_text))
            self.rob_table.setItem(i, 1, QTableWidgetItem('Sim' if entry.busy else 'Não'))
            self.rob_table.setItem(i, 2, QTableWidgetItem(
                str(entry.instruction) if entry.instruction else '-'
            ))
            self.rob_table.setItem(i, 3, QTableWidgetItem(entry.state))
            self.rob_table.setItem(i, 4, QTableWidgetItem(str(entry.dest) if entry.dest else '-'))
            self.rob_table.setItem(i, 5, QTableWidgetItem(str(entry.value) if entry.value is not None else '-'))
            self.rob_table.setItem(i, 6, QTableWidgetItem('Sim' if entry.ready else 'Não'))
            
            # Colorir
            if entry.busy:
                if i == self.simulator.rob_head:
                    color = QColor(255, 255, 150)  # Amarelo para head
                elif entry.speculative:
                    color = QColor(255, 200, 150)  # Laranja para especulativo
                else:
                    color = QColor(200, 200, 255)  # Azul claro para ativo
            else:
                color = QColor(240, 240, 240)  # Cinza para livre
                
            for j in range(7):
                item = self.rob_table.item(i, j)
                if item:
                    item.setBackground(color)
                    
        self.rob_table.resizeColumnsToContents()
        
    def update_registers_table(self):
        """Atualiza a tabela de registradores"""
        # Mostrar primeiros 16 registradores em 2 colunas
        self.registers_table.setRowCount(8)
        
        for i in range(8):
            # Coluna 1
            reg1 = f'R{i}'
            val1 = self.simulator.registers.get(reg1, 0)
            self.registers_table.setItem(i, 0, QTableWidgetItem(reg1))
            self.registers_table.setItem(i, 1, QTableWidgetItem(str(val1)))
            
            # Coluna 2
            reg2 = f'R{i+8}'
            val2 = self.simulator.registers.get(reg2, 0)
            self.registers_table.setItem(i, 2, QTableWidgetItem(reg2))
            self.registers_table.setItem(i, 3, QTableWidgetItem(str(val2)))
            
        self.registers_table.resizeColumnsToContents()
        
    def update_metrics(self):
        """Atualiza as métricas"""
        metrics = self.simulator.metrics
        bp = self.simulator.branch_predictor
        
        text = f"""Ciclo Atual: {self.simulator.current_cycle}
Instruções Despachadas: {metrics.instructions_issued}
Instruções Completadas: {metrics.instructions_completed}
IPC: {metrics.get_ipc():.3f}

Ciclos de Bolha: {metrics.bubble_cycles}
Ciclos de Stall: {metrics.stall_cycles}

Preditor de Desvios:
  Predições: {bp.predictions}
  Corretas: {bp.correct_predictions}
  Taxa de Acerto: {bp.get_accuracy()*100:.1f}%
  Mispredictions: {metrics.branch_mispredictions}
"""
        self.metrics_text.setPlainText(text)
        
    def _get_stage_color(self, stage):
        """Retorna cor baseada no estágio"""
        colors = {
            'Aguardando': QColor(240, 240, 240),
            'Despachada': QColor(200, 220, 255),
            'Executando': QColor(255, 255, 150),
            'Escrita de Resultado': QColor(200, 255, 200),
            'Commit': QColor(150, 255, 150),
        }
        return colors.get(stage.value, QColor(255, 255, 255))
