# Arquitetura do Simulador de Tomasulo

## Sumário
1. [Visão Geral](#visão-geral)
2. [O Algoritmo de Tomasulo](#o-algoritmo-de-tomasulo)
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Implementação Detalhada](#implementação-detalhada)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Métricas de Desempenho](#métricas-de-desempenho)

## Visão Geral

Este projeto implementa um **simulador do Algoritmo de Tomasulo**, uma técnica de execução fora de ordem (out-of-order execution) que permite o paralelismo em nível de instrução (ILP - Instruction Level Parallelism).

### Características Principais
- Execução fora de ordem com Estações de Reserva
- Renomeação de registradores dinâmica
- Reorder Buffer (ROB) para commit em ordem
- Especulação de desvios com preditor de 2 bits
- Interface gráfica
- Execução passo a passo
- Métricas de desempenho detalhadas
- Suporte a instruções MIPS

## O Algoritmo de Tomasulo

### Contexto Histórico
O algoritmo de Tomasulo foi desenvolvido por **Robert Tomasulo** na IBM em 1967 para o computador IBM 360/91. Foi uma das primeiras implementações de execução fora de ordem e continua sendo fundamental em processadores modernos.

### Problema que Resolve
Em pipelines tradicionais, **hazards** (conflitos) podem causar paradas:
- **RAW (Read After Write)**: Uma instrução precisa ler um dado que outra ainda não escreveu
- **WAR (Write After Read)**: Uma instrução precisa escrever antes que outra leia o valor antigo
- **WAW (Write After Write)**: Duas instruções escrevem no mesmo registrador

**Tomasulo resolve esses problemas através de:**
1. **Renomeação de Registradores**: Elimina dependências WAR e WAW
2. **Estações de Reserva**: Armazenam operandos e instruções esperando execução
3. **Common Data Bus (CDB)**: Propaga resultados para todas as unidades
4. **Reorder Buffer**: Garante commit em ordem (especulação segura)

### Componentes Principais

#### 1. Estações de Reserva (Reservation Stations)
Cada unidade funcional tem estações de reserva associadas:
- **ADD/SUB**: Operações aritméticas inteiras e de ponto flutuante
- **MUL/DIV**: Multiplicação e divisão
- **LOAD/STORE**: Acesso à memória

**Estrutura de uma Estação:**
```python
{
    'busy': bool,           # Está ocupada?
    'op': str,              # Operação (ADD, MUL, LOAD, etc)
    'vj': float,            # Valor do operando J
    'vk': float,            # Valor do operando K
    'qj': str,              # Tag da estação que produzirá Vj
    'qk': str,              # Tag da estação que produzirá Vk
    'dest': str,            # Registrador destino
    'a': int,               # Endereço de memória (LOAD/STORE)
    'rob_entry': int        # Entrada no ROB
}
```

#### 2. Reorder Buffer (ROB)
Mantém o estado das instruções em execução e garante commit em ordem:
```python
{
    'instruction': str,     # Instrução original
    'state': str,           # ISSUE, EXECUTE, WRITE, COMMIT
    'dest': str,            # Registrador destino
    'value': float,         # Resultado (quando pronto)
    'ready': bool,          # Resultado disponível?
    'pc': int               # Program Counter
}
```

#### 3. Register Status Table
Rastreia qual estação de reserva ou entrada ROB produzirá o valor de cada registrador:
```python
{
    'R0': None,    # Nenhuma dependência
    'R1': 'ROB3',  # Aguardando ROB entry 3
    'F2': 'Add1',  # Aguardando estação Add1
    ...
}
```

#### 4. Preditor de Desvios
Implementação de preditor de 2 bits (saturating counter):
```
Máquina de Estados:
    SNT --0--> WNT --0--> WT --0--> ST
     │          │         │         │
     |____1____-|____1____|____1____|

SNT = Strongly Not Taken
WNT = Weakly Not Taken  
WT  = Weakly Taken
ST  = Strongly Taken
```

### Ciclo de Vida de uma Instrução

```
1. ISSUE (Despacho)
   ├─ Verifica estação de reserva livre
   ├─ Verifica entrada ROB livre
   ├─ Lê operandos ou tags de dependência
   └─ Insere na estação e no ROB

2. EXECUTE (Execução)
   ├─ Espera operandos ficarem prontos
   ├─ Executa operação na unidade funcional
   └─ Considera latência da operação

3. WRITE RESULT (Escrita)
   ├─ Escreve resultado no CDB
   ├─ Atualiza todas as estações esperando
   ├─ Atualiza entrada no ROB
   └─ Libera estação de reserva

4. COMMIT
   ├─ Espera ser head do ROB
   ├─ Espera resultado estar pronto
   ├─ Atualiza arquivo de registradores
   ├─ Trata desvios (especulação)
   └─ Libera entrada do ROB
```

### Separação de Responsabilidades

#### **core/simulator.py** - Motor do Tomasulo
- Gerencia ciclos de clock
- Implementa os 4 estágios (Issue, Execute, Write, Commit)
- Controla hazards estruturais
- Gerencia especulação de desvios
- Calcula métricas de desempenho

#### **core/structures.py** - Estruturas de Dados
- `ReservationStation`: Estações de reserva
- `ReorderBuffer`: Buffer de reordenamento
- `RegisterFile`: Arquivo de registradores
- `Memory`: Memória principal
- `BranchPredictor`: Preditor de desvios

#### **mips/parser.py** - Parser MIPS
- Converte assembly MIPS para formato interno
- Valida sintaxe
- Suporta labels e desvios
- Trata pseudo-instruções

#### **gui/main_window.py** - Interface Gráfica
- Visualização de todas as estruturas
- Execução passo a passo
- Gráficos de métricas
- Timeline de instruções
- Console de log


## Implementação Detalhada

### 1. Estruturas de Dados Core

#### ReservationStation
```python
class ReservationStation:
    def __init__(self, name, num_stations, op_type, latency):
        self.name = name              # Ex: "Add", "Mult", "Load"
        self.num_stations = num_stations  # Número de estações
        self.op_type = op_type        # Tipo de operação
        self.latency = latency        # Ciclos de latência
        self.stations = []            # Lista de estações
        
    def get_free_station(self):
        """Retorna índice de estação livre ou None"""
        
    def issue_instruction(self, op, vj, vk, qj, qk, dest, rob_entry):
        """Despacha instrução para estação livre"""
        
    def can_execute(self, idx):
        """Verifica se instrução pode executar (operandos prontos)"""
        
    def execute(self, idx):
        """Executa operação e retorna resultado"""
```

#### ReorderBuffer
```python
class ReorderBuffer:
    def __init__(self, size):
        self.size = size              # Tamanho do ROB
        self.entries = []             # Entradas circulares
        self.head = 0                 # Próxima a fazer commit
        self.tail = 0                 # Próxima entrada livre
        
    def is_full(self):
        """Verifica se ROB está cheio"""
        
    def add_entry(self, instruction, dest, pc):
        """Adiciona nova entrada no tail"""
        
    def commit_head(self):
        """Faz commit da entrada no head"""
        
    def flush_from(self, pc):
        """Descarta instruções após PC (branch misprediction)"""
```

#### BranchPredictor
```python
class BranchPredictor:
    def __init__(self):
        self.prediction_table = {}    # PC -> estado (0-3)
        # 0=SNT, 1=WNT, 2=WT, 3=ST
        
    def predict(self, pc):
        """Retorna predição (True=Taken, False=Not Taken)"""
        
    def update(self, pc, taken):
        """Atualiza preditor com resultado real"""
```

### 2. Pipeline de 4 Estágios

#### Estágio 1: ISSUE (Despacho)
```python
def issue_stage(self):
    # Verifica paradas estruturais
    if self.rob.is_full():
        self.metrics['structural_hazards'] += 1
        return
        
    # Busca próxima instrução
    if self.pc < len(self.instructions):
        inst = self.instructions[self.pc]
        
        # Encontra estação de reserva apropriada
        rs = self.get_reservation_station(inst['op'])
        if not rs.has_free_station():
            self.metrics['structural_hazards'] += 1
            return
            
        # Lê operandos do register status
        vj, qj = self.read_operand(inst['rs'])
        vk, qk = self.read_operand(inst['rt'])
        
        # Adiciona ao ROB
        rob_entry = self.rob.add_entry(inst, inst['rd'], self.pc)
        
        # Despacha para estação de reserva
        rs.issue_instruction(inst['op'], vj, vk, qj, qk, inst['rd'], rob_entry)
        
        # Atualiza register status
        self.register_status[inst['rd']] = f"ROB{rob_entry}"
        
        # Trata desvios (especulação)
        if inst['op'] in ['BEQ', 'BNE']:
            prediction = self.branch_predictor.predict(self.pc)
            if prediction:
                self.pc = inst['target']  # Especula que desvia
            else:
                self.pc += 1
        else:
            self.pc += 1
```

#### Estágio 2: EXECUTE (Execução)
```python
def execute_stage(self):
    # Para cada estação de reserva
    for rs_name, rs in self.reservation_stations.items():
        for i, station in enumerate(rs.stations):
            if not station['busy']:
                continue
                
            # Verifica se operandos estão prontos
            if station['qj'] or station['qk']:
                continue  # Ainda esperando operandos
                
            # Verifica se já está executando
            if station['executing']:
                station['cycles_left'] -= 1
                if station['cycles_left'] == 0:
                    # Execução completa
                    result = self.compute_result(station)
                    self.write_queue.append({
                        'station': f"{rs_name}{i}",
                        'result': result,
                        'rob_entry': station['rob_entry']
                    })
                continue
                
            # Inicia execução
            station['executing'] = True
            station['cycles_left'] = rs.latency
            
            # Atualiza estado no ROB
            self.rob.entries[station['rob_entry']]['state'] = 'EXECUTE'
```

#### Estágio 3: WRITE RESULT (Escrita no CDB)
```python
def write_result_stage(self):
    # Simula Common Data Bus (apenas 1 escrita por ciclo)
    if not self.write_queue:
        return
        
    write_op = self.write_queue.pop(0)
    
    # Atualiza ROB
    rob_entry = write_op['rob_entry']
    self.rob.entries[rob_entry]['value'] = write_op['result']
    self.rob.entries[rob_entry]['ready'] = True
    self.rob.entries[rob_entry]['state'] = 'WRITE'
    
    # Broadcast no CDB - atualiza todas as estações esperando
    for rs in self.reservation_stations.values():
        for station in rs.stations:
            if station['qj'] == write_op['station']:
                station['vj'] = write_op['result']
                station['qj'] = None
            if station['qk'] == write_op['station']:
                station['vk'] = write_op['result']
                station['qk'] = None
    
    # Libera estação de reserva
    self.free_station(write_op['station'])
```

#### Estágio 4: COMMIT
```python
def commit_stage(self):
    # Apenas commit da head do ROB (em ordem)
    if self.rob.is_empty():
        return
        
    head_entry = self.rob.entries[self.rob.head]
    
    # Verifica se está pronta
    if not head_entry['ready']:
        return
        
    # Trata desvios (verifica especulação)
    if head_entry['instruction']['op'] in ['BEQ', 'BNE']:
        prediction = self.branch_predictor.predict(head_entry['pc'])
        actual_taken = self.evaluate_branch(head_entry)
        
        if prediction != actual_taken:
            # Misprediction!
            self.metrics['branch_mispredictions'] += 1
            self.flush_pipeline(head_entry['pc'])
            if actual_taken:
                self.pc = head_entry['instruction']['target']
            else:
                self.pc = head_entry['pc'] + 1
                
        # Atualiza preditor
        self.branch_predictor.update(head_entry['pc'], actual_taken)
    else:
        # Instrução normal - commit
        self.registers[head_entry['dest']] = head_entry['value']
        
        # Atualiza register status (se ainda apontando para este ROB)
        if self.register_status[head_entry['dest']] == f"ROB{self.rob.head}":
            self.register_status[head_entry['dest']] = None
    
    # Avança head do ROB
    head_entry['state'] = 'COMMIT'
    self.rob.head = (self.rob.head + 1) % self.rob.size
    self.metrics['instructions_committed'] += 1
```

### 3. Métricas de Desempenho

```python
class PerformanceMetrics:
    def __init__(self):
        self.total_cycles = 0
        self.instructions_issued = 0
        self.instructions_committed = 0
        self.structural_hazards = 0      # ROB/RS cheios
        self.data_hazards = 0             # RAW delays
        self.branch_mispredictions = 0
        self.bubble_cycles = 0            # Ciclos sem issue
        
    def calculate_ipc(self):
        """Instructions Per Cycle"""
        if self.total_cycles == 0:
            return 0
        return self.instructions_committed / self.total_cycles
        
    def calculate_efficiency(self):
        """Percentual de ciclos produtivos"""
        if self.total_cycles == 0:
            return 0
        productive = self.total_cycles - self.bubble_cycles
        return (productive / self.total_cycles) * 100
```

### 4. Interface Gráfica

A GUI é dividida em várias seções para facilitar o aprendizado:

#### Componentes Visuais

**1. Painel de Controle**
- Run: Execução completa
- Step: Execução passo a passo
- Pause: Pausa execução
- Stop: Para e reseta
- Speed: Controle de velocidade

**2. Visualização de Instruções**
```
PC | Instruction      | State   | Issue | Exec | Write | Commit
---+------------------+---------+-------+------+-------+--------
0  | ADD F0, F2, F4   | COMMIT  |   1   |  2   |   4   |   5
1  | MUL F6, F0, F8   | WRITE   |   2   |  3   |   7   |   -
2  | SUB F8, F2, F6   | EXECUTE |   3   |  5   |   -   |   -
```

**3. Estações de Reserva**
```
Add1  | Busy | Op  | Vj  | Vk  | Qj   | Qk   | Dest | ROB
------+------+-----+-----+-----+------+------+------+-----
  0   |  ✓   | ADD | 2.0 | 4.0 | -    | -    | F0   | 0
  1   |  ✓   | SUB | 2.0 | -   | -    | ROB1 | F8   | 2
  2   |  ✗   | -   | -   | -   | -    | -    | -    | -
```

**4. Reorder Buffer**
```
Entry | Instruction    | State   | Dest | Value | Ready
------+----------------+---------+------+-------+-------
  0   | ADD F0, F2, F4 | COMMIT  | F0   | 6.0   |  ✓
  1   | MUL F6, F0, F8 | WRITE   | F6   | 48.0  |  ✓
  2   | SUB F8, F2, F6 | EXECUTE | F8   | -     |  ✗
```

**5. Registradores e Memória**
- Arquivo de registradores com status
- Memória com endereços e valores
- Destacamento de mudanças recentes

**6. Métricas em Tempo Real**
- Gráfico de IPC ao longo do tempo
- Contadores de hazards
- Estatísticas de predição de desvios

## Métricas de Desempenho

### 1. IPC (Instructions Per Cycle)
```
IPC = Instruções Committed / Total de Ciclos
```
**Objetivo**: Quanto maior, melhor. IPC > 1 indica paralelismo efetivo.

### 2. Ciclos de Bolha (Bubble Cycles)
Ciclos onde nenhuma instrução foi despachada devido a:
- ROB cheio (hazard estrutural)
- Todas as estações de reserva ocupadas
- Branch misprediction recovery

### 3. Taxa de Acerto de Predição de Desvios
```
Hit Rate = (Predições Corretas / Total de Desvios) * 100%
```

### 4. Utilização de Recursos
```
Utilização RS = (Ciclos com RS ocupada / Total de Ciclos) * 100%
Utilização ROB = (Entradas usadas / Tamanho ROB) * 100%
```

### 5. Breakdown de Hazards
- **Estruturais**: ROB/RS cheios
- **Dados (RAW)**: Dependências verdadeiras
- **Controle**: Branch mispredictions
