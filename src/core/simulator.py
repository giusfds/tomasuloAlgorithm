"""
Simulador do Algoritmo de Tomasulo
"""
from typing import List, Dict, Optional
from src.core.structures import (
    Instruction, InstructionType, InstructionStage,
    ReservationStation, ROBEntry, RegisterStatus,
    BranchPredictor, PerformanceMetrics
)


class TomasuloSimulator:
    """Simulador do algoritmo de Tomasulo com ROB e especulação"""
    
    def __init__(self, config: Dict = None):
        """
        Inicializa o simulador
        
        Args:
            config: Configuração com número de reservation stations, latências, etc.
        """
        if config is None:
            config = {}
            
        # Configuração
        self.num_add_rs = config.get('add_rs', 3)
        self.num_mul_rs = config.get('mul_rs', 2)
        self.num_load_rs = config.get('load_rs', 2)
        self.num_store_rs = config.get('store_rs', 2)
        self.rob_size = config.get('rob_size', 16)
        
        # Latências de execução
        self.latencies = {
            InstructionType.ADD: config.get('add_latency', 2),
            InstructionType.SUB: config.get('sub_latency', 2),
            InstructionType.ADDI: config.get('addi_latency', 2),
            InstructionType.MUL: config.get('mul_latency', 10),
            InstructionType.DIV: config.get('div_latency', 20),
            InstructionType.LW: config.get('lw_latency', 3),
            InstructionType.SW: config.get('sw_latency', 3),
            InstructionType.BEQ: config.get('beq_latency', 1),
            InstructionType.BNE: config.get('bne_latency', 1),
            InstructionType.J: config.get('j_latency', 1),
        }
        
        # Estruturas do Tomasulo
        self.add_rs: List[ReservationStation] = []
        self.mul_rs: List[ReservationStation] = []
        self.load_rs: List[ReservationStation] = []
        self.store_rs: List[ReservationStation] = []
        
        self._initialize_rs()
        
        # Reorder Buffer
        self.rob: List[ROBEntry] = [ROBEntry(i) for i in range(self.rob_size)]
        self.rob_head = 0  # Próxima entrada para commit
        self.rob_tail = 0  # Próxima entrada livre
        
        # Register Status Table
        self.register_status = RegisterStatus()
        
        # Registradores (32 registradores MIPS)
        self.registers = {f'R{i}': 0 for i in range(32)}
        self.registers['R0'] = 0  # R0 sempre zero
        
        # Memória (simplificada)
        self.memory = {}
        
        # Branch Predictor
        self.branch_predictor = BranchPredictor()
        
        # Controle de execução
        self.instructions: List[Instruction] = []
        self.pc = 0
        self.current_cycle = 0
        self.finished = False
        
        # Métricas
        self.metrics = PerformanceMetrics()
        
        # Controle de especulação
        self.speculating = False
        self.speculation_rob = None  # ROB entry do desvio especulativo
        
    def _initialize_rs(self):
        """Inicializa as reservation stations"""
        for i in range(self.num_add_rs):
            self.add_rs.append(ReservationStation(f'Add{i+1}', 'Add'))
        for i in range(self.num_mul_rs):
            self.mul_rs.append(ReservationStation(f'Mult{i+1}', 'Mult'))
        for i in range(self.num_load_rs):
            self.load_rs.append(ReservationStation(f'Load{i+1}', 'Load'))
        for i in range(self.num_store_rs):
            self.store_rs.append(ReservationStation(f'Store{i+1}', 'Store'))
            
    def load_program(self, instructions: List[Instruction]):
        """Carrega um programa para execução"""
        self.instructions = instructions
        self.reset()
        
    def reset(self):
        """Reseta o simulador"""
        # Limpar reservation stations
        for rs in self.add_rs + self.mul_rs + self.load_rs + self.store_rs:
            rs.clear()
            
        # Limpar ROB
        for entry in self.rob:
            entry.clear()
        self.rob_head = 0
        self.rob_tail = 0
        
        # Limpar status de registradores
        self.register_status = RegisterStatus()
        
        # Resetar registradores
        self.registers = {f'R{i}': 0 for i in range(32)}
        
        # Resetar controle
        self.pc = 0
        self.current_cycle = 0
        self.finished = False
        self.speculating = False
        self.speculation_rob = None
        
        # Resetar métricas
        self.metrics = PerformanceMetrics()
        
    def step(self):
        """Executa um ciclo do simulador"""
        if self.finished:
            return False
            
        self.current_cycle += 1
        self.metrics.total_cycles += 1
        
        # 1. Commit (primeiro para liberar recursos)
        self._commit_stage()
        
        # 2. Write Result (broadcast de resultados)
        self._write_result_stage()
        
        # 3. Execute (execução de instruções prontas)
        self._execute_stage()
        
        # 4. Issue (despacho de novas instruções)
        self._issue_stage()
        
        # Verificar se terminou
        if self._is_finished():
            self.finished = True
            return False
            
        return True
        
    def _issue_stage(self):
        """Estágio de Issue - despacha instruções para RS e ROB"""
        # Verificar se há espaço no ROB
        if self._rob_full():
            return
            
        # Verificar se ainda há instruções para despachar
        if self.pc >= len(self.instructions):
            return
            
        inst = self.instructions[self.pc]
        
        # Obter reservation station apropriada
        rs = self._get_free_rs(inst.type)
        if rs is None:
            self.metrics.stall_cycles += 1
            return
            
        # Alocar entrada no ROB
        rob_entry = self._allocate_rob()
        if rob_entry is None:
            return
            
        # Configurar ROB entry
        rob_entry.busy = True
        rob_entry.instruction = inst
        rob_entry.state = "Issue"
        
        # Marcar se é especulativa
        if self.speculating:
            rob_entry.speculative = True
            
        # Configurar destino
        if inst.type in [InstructionType.ADD, InstructionType.SUB, 
                        InstructionType.MUL, InstructionType.DIV,
                        InstructionType.ADDI, InstructionType.LW]:
            rob_entry.dest = inst.dest
            # Atualizar register status
            self.register_status.set_dependency(inst.dest, rob_entry.entry_id)
        elif inst.type == InstructionType.SW:
            rob_entry.dest = f"Mem[{inst.offset}]"
            
        # Configurar reservation station
        rs.busy = True
        rs.op = inst.type
        rs.dest = rob_entry.entry_id
        rs.instruction = inst
        rs.cycles_remaining = self.latencies.get(inst.type, 1)
        
        # Obter valores dos operandos
        self._setup_operands(rs, inst, rob_entry)
        
        # Atualizar instrução
        inst.issue_cycle = self.current_cycle
        inst.stage = InstructionStage.ISSUED
        inst.rob_entry = rob_entry.entry_id
        inst.rs_entry = rs.name
        
        # Especulação de desvios
        if inst.type in [InstructionType.BEQ, InstructionType.BNE]:
            predicted = self.branch_predictor.predict(inst.pc)
            rob_entry.branch_predicted = predicted
            
            if predicted:
                # Desvio predito como tomado - começar especulação
                self.speculating = True
                self.speculation_rob = rob_entry.entry_id
                # Calcular novo PC (simplificado - usa label)
                # Em implementação real, calcularia o endereço
                
        # Avançar PC
        self.pc += 1
        self.metrics.instructions_issued += 1
        
    def _execute_stage(self):
        """Estágio de Execute - executa instruções prontas"""
        all_rs = self.add_rs + self.mul_rs + self.load_rs + self.store_rs
        
        for rs in all_rs:
            if not rs.busy:
                continue
                
            # Verificar se está pronta para executar
            if rs.is_ready():
                if rs.cycles_remaining > 0:
                    rs.cycles_remaining -= 1
                    if rs.instruction:
                        rs.instruction.stage = InstructionStage.EXECUTING
                        if rs.instruction.exec_start_cycle is None:
                            rs.instruction.exec_start_cycle = self.current_cycle
                            
                # Se terminou execução
                if rs.cycles_remaining == 0:
                    self._execute_operation(rs)
                    if rs.instruction:
                        rs.instruction.exec_end_cycle = self.current_cycle
                        
    def _execute_operation(self, rs: ReservationStation):
        """Executa a operação e calcula o resultado"""
        inst = rs.instruction
        rob_entry = self.rob[rs.dest]
        
        if inst.type == InstructionType.ADD:
            rob_entry.value = rs.vj + rs.vk
            rob_entry.ready = True
        elif inst.type == InstructionType.SUB:
            rob_entry.value = rs.vj - rs.vk
            rob_entry.ready = True
        elif inst.type == InstructionType.MUL:
            rob_entry.value = rs.vj * rs.vk
            rob_entry.ready = True
        elif inst.type == InstructionType.DIV:
            rob_entry.value = rs.vj // rs.vk if rs.vk != 0 else 0
            rob_entry.ready = True
        elif inst.type == InstructionType.ADDI:
            rob_entry.value = rs.vj + inst.immediate
            rob_entry.ready = True
        elif inst.type == InstructionType.LW:
            address = rs.vj + inst.offset
            rob_entry.value = self.memory.get(address, 0)
            rob_entry.ready = True
        elif inst.type == InstructionType.SW:
            address = rs.vj + inst.offset
            rs.address = address
            rob_entry.value = rs.vk  # Valor a armazenar
            rob_entry.ready = True
        elif inst.type in [InstructionType.BEQ, InstructionType.BNE]:
            # Avaliar condição de desvio
            if inst.type == InstructionType.BEQ:
                taken = (rs.vj == rs.vk)
            else:  # BNE
                taken = (rs.vj != rs.vk)
                
            rob_entry.branch_actual = taken
            rob_entry.ready = True
            
            # Atualizar preditor
            self.branch_predictor.update(inst.pc, taken)
            
            # Verificar misprediction
            if rob_entry.branch_predicted != taken:
                self.metrics.branch_mispredictions += 1
                # O flush será feito no commit
                
        rob_entry.state = "Write"
        
    def _write_result_stage(self):
        """Estágio de Write Result - broadcast de resultados"""
        all_rs = self.add_rs + self.mul_rs + self.load_rs + self.store_rs
        
        for rs in all_rs:
            if not rs.busy:
                continue
                
            rob_entry = self.rob[rs.dest]
            
            # Se o resultado está pronto e ainda não foi escrito
            if rob_entry.ready and rob_entry.state == "Write":
                # Broadcast para outras reservation stations
                for other_rs in all_rs:
                    if other_rs.busy:
                        if other_rs.qj == rs.dest:
                            other_rs.vj = rob_entry.value
                            other_rs.qj = None
                        if other_rs.qk == rs.dest:
                            other_rs.vk = rob_entry.value
                            other_rs.qk = None
                            
                # Marcar como escrito
                rob_entry.state = "Commit"
                if rs.instruction:
                    rs.instruction.write_cycle = self.current_cycle
                    rs.instruction.stage = InstructionStage.WRITE_RESULT
                    
                # Liberar reservation station
                rs.clear()
                
    def _commit_stage(self):
        """Estágio de Commit - commit em ordem"""
        rob_entry = self.rob[self.rob_head]
        
        if not rob_entry.busy or rob_entry.state != "Commit":
            self.metrics.bubble_cycles += 1
            return
            
        inst = rob_entry.instruction
        
        # Verificar misprediction de desvio
        if inst.type in [InstructionType.BEQ, InstructionType.BNE]:
            if rob_entry.branch_predicted != rob_entry.branch_actual:
                # Flush de instruções especulativas
                self._flush_speculative_instructions()
                # Corrigir PC
                # (simplificado - em implementação real calcularia endereço correto)
                self.speculating = False
                self.speculation_rob = None
                
        # Commit baseado no tipo de instrução
        if inst.type in [InstructionType.ADD, InstructionType.SUB,
                        InstructionType.MUL, InstructionType.DIV,
                        InstructionType.ADDI, InstructionType.LW]:
            # Escrever no registrador
            if rob_entry.dest:
                self.registers[rob_entry.dest] = rob_entry.value
                # Limpar dependência se ainda aponta para este ROB
                if self.register_status.get_producer(rob_entry.dest) == rob_entry.entry_id:
                    self.register_status.clear_dependency(rob_entry.dest)
                    
        elif inst.type == InstructionType.SW:
            # Escrever na memória
            # Encontrar o endereço calculado
            for rs in self.store_rs:
                if rs.instruction == inst and rs.address is not None:
                    self.memory[rs.address] = rob_entry.value
                    break
                    
        # Atualizar instrução
        inst.commit_cycle = self.current_cycle
        inst.stage = InstructionStage.COMMIT
        
        # Liberar ROB entry
        rob_entry.clear()
        self.rob_head = (self.rob_head + 1) % self.rob_size
        
        self.metrics.instructions_completed += 1
        
    def _setup_operands(self, rs: ReservationStation, inst: Instruction, rob_entry: ROBEntry):
        """Configura os operandos da reservation station"""
        # Operando J (src1)
        if inst.src1:
            producer = self.register_status.get_producer(inst.src1)
            if producer is not None:
                # Há dependência - verificar se valor já está pronto
                if self.rob[producer].ready:
                    rs.vj = self.rob[producer].value
                else:
                    rs.qj = producer
            else:
                # Sem dependência - usar valor do registrador
                rs.vj = self.registers.get(inst.src1, 0)
                
        # Operando K (src2)
        if inst.src2:
            producer = self.register_status.get_producer(inst.src2)
            if producer is not None:
                if self.rob[producer].ready:
                    rs.vk = self.rob[producer].value
                else:
                    rs.qk = producer
            else:
                rs.vk = self.registers.get(inst.src2, 0)
                
    def _get_free_rs(self, inst_type: InstructionType) -> Optional[ReservationStation]:
        """Retorna uma reservation station livre do tipo apropriado"""
        if inst_type in [InstructionType.ADD, InstructionType.SUB, InstructionType.ADDI]:
            for rs in self.add_rs:
                if not rs.busy:
                    return rs
        elif inst_type in [InstructionType.MUL, InstructionType.DIV]:
            for rs in self.mul_rs:
                if not rs.busy:
                    return rs
        elif inst_type == InstructionType.LW:
            for rs in self.load_rs:
                if not rs.busy:
                    return rs
        elif inst_type == InstructionType.SW:
            for rs in self.store_rs:
                if not rs.busy:
                    return rs
        elif inst_type in [InstructionType.BEQ, InstructionType.BNE]:
            # Desvios podem usar Add RS
            for rs in self.add_rs:
                if not rs.busy:
                    return rs
        return None
        
    def _rob_full(self) -> bool:
        """Verifica se o ROB está cheio"""
        next_tail = (self.rob_tail + 1) % self.rob_size
        return next_tail == self.rob_head and self.rob[self.rob_tail].busy
        
    def _allocate_rob(self) -> Optional[ROBEntry]:
        """Aloca uma entrada do ROB"""
        if self._rob_full():
            return None
            
        entry = self.rob[self.rob_tail]
        self.rob_tail = (self.rob_tail + 1) % self.rob_size
        return entry
        
    def _flush_speculative_instructions(self):
        """Limpa instruções especulativas após misprediction"""
        # Limpar reservation stations com instruções especulativas
        for rs in self.add_rs + self.mul_rs + self.load_rs + self.store_rs:
            if rs.busy and rs.instruction and rs.instruction.rob_entry is not None:
                rob_entry = self.rob[rs.instruction.rob_entry]
                if rob_entry.speculative:
                    rs.clear()
                    
        # Limpar ROB entries especulativas
        for entry in self.rob:
            if entry.busy and entry.speculative:
                # Limpar dependências de registradores
                if entry.dest and entry.dest.startswith('R'):
                    if self.register_status.get_producer(entry.dest) == entry.entry_id:
                        self.register_status.clear_dependency(entry.dest)
                entry.clear()
                
        # Ajustar ROB tail
        # (simplificado - em implementação real seria mais complexo)
        
    def _is_finished(self) -> bool:
        """Verifica se a simulação terminou"""
        # Terminou se todas as instruções foram despachadas e ROB está vazio
        if self.pc >= len(self.instructions):
            for entry in self.rob:
                if entry.busy:
                    return False
            return True
        return False
        
    def run_until_complete(self):
        """Executa até completar todas as instruções"""
        while not self.finished:
            self.step()
            # Proteção contra loop infinito
            if self.current_cycle > 10000:
                print("Aviso: Simulação excedeu 10000 ciclos")
                break
                
    def get_state_snapshot(self) -> Dict:
        """Retorna um snapshot do estado atual do simulador"""
        return {
            'cycle': self.current_cycle,
            'pc': self.pc,
            'registers': dict(self.registers),
            'memory': dict(self.memory),
            'add_rs': [str(rs) for rs in self.add_rs],
            'mul_rs': [str(rs) for rs in self.mul_rs],
            'load_rs': [str(rs) for rs in self.load_rs],
            'store_rs': [str(rs) for rs in self.store_rs],
            'rob': [str(entry) for entry in self.rob],
            'rob_head': self.rob_head,
            'rob_tail': self.rob_tail,
            'metrics': str(self.metrics),
            'finished': self.finished
        }
