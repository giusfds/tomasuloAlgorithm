"""
Estruturas de dados para o simulador de Tomasulo
"""
from enum import Enum
from typing import Optional, List


class InstructionType(Enum):
    """Tipos de instrução suportadas"""
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    ADDI = "ADDI"
    LW = "LW"
    SW = "SW"
    BEQ = "BEQ"
    BNE = "BNE"
    J = "J"
    NOP = "NOP"


class InstructionStage(Enum):
    """Estágios de execução de uma instrução"""
    WAITING = "Aguardando"
    ISSUED = "Despachada"
    EXECUTING = "Executando"
    WRITE_RESULT = "Escrita de Resultado"
    COMMIT = "Commit"


class Instruction:
    """Representa uma instrução MIPS"""
    def __init__(self, inst_type: InstructionType, dest: str = None, 
                 src1: str = None, src2: str = None, immediate: int = None,
                 offset: int = None, label: str = None, pc: int = 0):
        self.type = inst_type
        self.dest = dest  # Registrador de destino
        self.src1 = src1  # Primeiro operando
        self.src2 = src2  # Segundo operando
        self.immediate = immediate  # Valor imediato
        self.offset = offset  # Offset para loads/stores
        self.label = label  # Label para desvios
        self.pc = pc  # Program counter
        
        # Informações de execução
        self.stage = InstructionStage.WAITING
        self.issue_cycle = None
        self.exec_start_cycle = None
        self.exec_end_cycle = None
        self.write_cycle = None
        self.commit_cycle = None
        self.rob_entry = None
        self.rs_entry = None
        
    def __str__(self):
        if self.type in [InstructionType.ADD, InstructionType.SUB, 
                         InstructionType.MUL, InstructionType.DIV]:
            return f"{self.type.value} {self.dest}, {self.src1}, {self.src2}"
        elif self.type == InstructionType.ADDI:
            return f"ADDI {self.dest}, {self.src1}, {self.immediate}"
        elif self.type == InstructionType.LW:
            return f"LW {self.dest}, {self.offset}({self.src1})"
        elif self.type == InstructionType.SW:
            return f"SW {self.src2}, {self.offset}({self.src1})"
        elif self.type in [InstructionType.BEQ, InstructionType.BNE]:
            return f"{self.type.value} {self.src1}, {self.src2}, {self.label}"
        elif self.type == InstructionType.J:
            return f"J {self.label}"
        return self.type.value


class ReservationStation:
    """Reservation Station para execução de instruções"""
    def __init__(self, name: str, op_type: str):
        self.name = name
        self.op_type = op_type  # 'Add', 'Mult', 'Load', 'Store'
        self.busy = False
        self.op = None  # Operação
        self.vj = None  # Valor do operando J
        self.vk = None  # Valor do operando K
        self.qj = None  # ROB entry que produzirá Vj
        self.qk = None  # ROB entry que produzirá Vk
        self.dest = None  # ROB entry de destino
        self.address = None  # Endereço para load/store
        self.instruction = None  # Referência para a instrução
        self.cycles_remaining = 0  # Ciclos restantes de execução
        
    def clear(self):
        """Limpa a reservation station"""
        self.busy = False
        self.op = None
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.dest = None
        self.address = None
        self.instruction = None
        self.cycles_remaining = 0
        
    def is_ready(self) -> bool:
        """Verifica se a instrução está pronta para executar"""
        return self.busy and self.qj is None and self.qk is None
        
    def __str__(self):
        if not self.busy:
            return f"{self.name}: Livre"
        return f"{self.name}: {self.op} Vj={self.vj} Vk={self.vk} Qj={self.qj} Qk={self.qk}"


class ROBEntry:
    """Entrada do Reorder Buffer"""
    def __init__(self, entry_id: int):
        self.entry_id = entry_id
        self.busy = False
        self.instruction = None
        self.state = "Issue"  # Issue, Execute, Write, Commit
        self.dest = None  # Registrador ou endereço de destino
        self.value = None  # Valor a ser escrito
        self.ready = False  # Se o valor está pronto
        self.speculative = False  # Se é uma instrução especulativa
        self.branch_predicted = None  # Para desvios: True (taken) / False (not taken)
        self.branch_actual = None  # Resultado real do desvio
        
    def clear(self):
        """Limpa a entrada do ROB"""
        self.busy = False
        self.instruction = None
        self.state = "Issue"
        self.dest = None
        self.value = None
        self.ready = False
        self.speculative = False
        self.branch_predicted = None
        self.branch_actual = None
        
    def __str__(self):
        if not self.busy:
            return f"ROB{self.entry_id}: Livre"
        inst_str = str(self.instruction) if self.instruction else "?"
        return f"ROB{self.entry_id}: {inst_str} | {self.state} | Dest={self.dest} | Value={self.value} | Ready={self.ready}"


class RegisterStatus:
    """Status dos registradores - rastreamento de dependências"""
    def __init__(self):
        # Mapeia nome do registrador para ROB entry que irá escrevê-lo
        self.reorder = {}
        
    def set_dependency(self, reg: str, rob_entry: int):
        """Define que o registrador será escrito pela entrada ROB"""
        self.reorder[reg] = rob_entry
        
    def clear_dependency(self, reg: str):
        """Remove a dependência do registrador"""
        if reg in self.reorder:
            del self.reorder[reg]
            
    def get_producer(self, reg: str) -> Optional[int]:
        """Retorna a entrada ROB que produzirá o valor do registrador"""
        return self.reorder.get(reg, None)
        
    def __str__(self):
        return str(self.reorder)


class BranchPredictor:
    """Preditor de desvios de 2 bits"""
    def __init__(self):
        # Tabela de predição: PC -> estado (0-3)
        # 0,1 = not taken, 2,3 = taken
        self.table = {}
        self.predictions = 0
        self.correct_predictions = 0
        
    def predict(self, pc: int) -> bool:
        """Prediz se o desvio será tomado"""
        state = self.table.get(pc, 1)  # Estado inicial: weakly not taken
        return state >= 2
        
    def update(self, pc: int, taken: bool):
        """Atualiza o preditor com o resultado real"""
        state = self.table.get(pc, 1)
        
        if taken:
            state = min(3, state + 1)
        else:
            state = max(0, state - 1)
            
        self.table[pc] = state
        
    def record_prediction(self, correct: bool):
        """Registra uma predição"""
        self.predictions += 1
        if correct:
            self.correct_predictions += 1
            
    def get_accuracy(self) -> float:
        """Retorna a taxa de acerto"""
        if self.predictions == 0:
            return 0.0
        return self.correct_predictions / self.predictions


class PerformanceMetrics:
    """Métricas de desempenho do simulador"""
    def __init__(self):
        self.total_cycles = 0
        self.instructions_issued = 0
        self.instructions_completed = 0
        self.bubble_cycles = 0
        self.stall_cycles = 0
        self.branch_mispredictions = 0
        
    def get_ipc(self) -> float:
        """Calcula IPC (Instructions Per Cycle)"""
        if self.total_cycles == 0:
            return 0.0
        return self.instructions_completed / self.total_cycles
        
    def __str__(self):
        return f"""Métricas de Desempenho:
  Total de Ciclos: {self.total_cycles}
  Instruções Despachadas: {self.instructions_issued}
  Instruções Completadas: {self.instructions_completed}
  IPC: {self.get_ipc():.2f}
  Ciclos de Bolha: {self.bubble_cycles}
  Ciclos de Stall: {self.stall_cycles}
  Mispredictions de Desvio: {self.branch_mispredictions}"""
