# Documentação Técnica - Simulador de Tomasulo

## Arquitetura do Simulador

### Componentes Principais

#### 1. Estruturas de Dados (`src/core/structures.py`)

**Instruction**
- Representa uma instrução MIPS
- Rastreia estágio de execução e ciclos
- Armazena informações de despacho, execução e commit

**ReservationStation**
- Buffer para instruções aguardando execução
- Armazena operandos ou referências para produtores
- Tipos: Add, Mult, Load, Store

**ROBEntry**
- Entrada do Reorder Buffer
- Mantém resultado até commit
- Suporta marcação de instruções especulativas

**RegisterStatus**
- Tabela de status de registradores
- Rastreia qual ROB entry produzirá cada registrador
- Implementa register renaming

**BranchPredictor**
- Preditor de 2 bits saturante
- Tabela indexada por PC
- Estados: 00 (strongly not taken) ... 11 (strongly taken)

**PerformanceMetrics**
- Coleta métricas de desempenho
- Calcula IPC, bolhas, stalls

#### 2. Simulador (`src/core/simulator.py`)

**Pipeline de 4 Estágios**:

1. **Issue**
   - Verifica espaço em RS e ROB
   - Lê status de registradores
   - Aloca recursos
   - Para desvios: faz predição e marca instruções subsequentes como especulativas

2. **Execute**
   - Instruções prontas executam
   - Decrementam contador de latência
   - Calculam resultados

3. **Write Result**
   - Broadcast de resultados
   - Atualiza dependências em outras RS
   - Libera RS

4. **Commit**
   - Commit em ordem (ROB head)
   - Escreve em registradores/memória
   - Para desvios: verifica predição
   - Se misprediction: flush de instruções especulativas

**Configuração**:
```python
config = {
    'add_rs': 3,      # Número de Add RS
    'mul_rs': 2,      # Número de Mult RS
    'load_rs': 2,     # Número de Load RS
    'store_rs': 2,    # Número de Store RS
    'rob_size': 16,   # Tamanho do ROB
    'add_latency': 2,
    'mul_latency': 10,
    'div_latency': 20,
    ...
}
```

#### 3. Parser MIPS (`src/mips/parser.py`)

**Formato de Instruções Suportadas**:

- `ADD/SUB/MUL/DIV rd, rs, rt`
- `ADDI rt, rs, imm`
- `LW rt, offset(rs)`
- `SW rt, offset(rs)`
- `BEQ/BNE rs, rt, label`
- `J label`

**Processo de Parse**:
1. Primeiro passo: identificar labels e seus PCs
2. Segundo passo: parse de instruções
3. Retorna lista de objetos Instruction

#### 4. Interface Gráfica (`src/gui/main_window.py`)

**Componentes da GUI**:

- **CodeEditor**: Editor de código MIPS com syntax highlighting básico
- **InstructionsTable**: Mostra pipeline de cada instrução
- **RSTable**: Estado atual das Reservation Stations
- **ROBTable**: Estado do Reorder Buffer
- **RegistersTable**: Valores dos registradores
- **MetricsPanel**: Estatísticas em tempo real

**Modos de Execução**:
- Step-by-step: Um ciclo por vez
- Run all: Até completar
- Auto-run: Automático com timer

## Algoritmo Detalhado

### Issue Stage

```python
if ROB_full() or no_free_RS():
    stall
else:
    allocate ROB_entry
    allocate RS
    
    for each source operand:
        if has_dependency():
            RS.Q = producer_ROB_entry
        else:
            RS.V = register_value
            
    if is_branch():
        predict()
        if predicted_taken:
            mark_subsequent_as_speculative()
            
    update_register_status()
    advance_PC()
```

### Execute Stage

```python
for each RS:
    if RS.is_ready():  # Qj == None and Qk == None
        if cycles_remaining > 0:
            cycles_remaining--
        else:
            execute_operation()
            ROB[RS.dest].value = result
            ROB[RS.dest].ready = True
```

### Write Result Stage

```python
for each RS:
    if ROB[RS.dest].ready and not_written_yet:
        # Broadcast
        for other_RS:
            if other_RS.Qj == RS.dest:
                other_RS.Vj = ROB[RS.dest].value
                other_RS.Qj = None
            if other_RS.Qk == RS.dest:
                other_RS.Vk = ROB[RS.dest].value
                other_RS.Qk = None
        
        free(RS)
```

### Commit Stage

```python
ROB_entry = ROB[head]

if ROB_entry.ready:
    if is_branch():
        if mispredicted:
            flush_speculative_instructions()
            restore_PC()
    
    write_to_register_or_memory()
    
    if register_status[dest] == ROB_entry:
        clear_dependency(dest)
    
    free(ROB_entry)
    advance_head()
```

## Especulação de Desvios

### Preditor de 2 Bits

Estado por PC:
- 00: Strongly Not Taken
- 01: Weakly Not Taken
- 10: Weakly Taken
- 11: Strongly Taken

Atualização:
- Desvio tomado: state = min(3, state + 1)
- Desvio não tomado: state = max(0, state - 1)

### Gerenciamento de Especulação

1. **Na Issue do Desvio**:
   - Faz predição
   - Se taken: marca próximas instruções como especulativas
   - Armazena ROB entry do desvio

2. **Durante Execução**:
   - Instruções especulativas executam normalmente
   - Resultados vão para ROB mas não fazem commit

3. **No Commit do Desvio**:
   - Se predição correta: continua normal
   - Se predição incorreta:
     - Flush de todas as instruções especulativas
     - Limpa RS com instruções especulativas
     - Limpa ROB entries especulativas
     - Restaura PC correto

## Métricas de Desempenho

### IPC (Instructions Per Cycle)
```python
IPC = instructions_completed / total_cycles
```

Ideal: próximo de 1.0 ou maior (com superescalar)

### Ciclos de Bolha
Ciclos onde ROB head não pode fazer commit (não está pronto)

### Ciclos de Stall
Ciclos onde nenhuma instrução é despachada (ROB cheio ou RS cheias)

### Taxa de Acerto de Desvios
```python
accuracy = correct_predictions / total_predictions
```

## Otimizações Implementadas

1. **Register Renaming via ROB**: Elimina WAR e WAW
2. **Forwarding via Broadcast**: Reduz latência de dependências
3. **Execução Fora de Ordem**: Maximiza utilização de unidades funcionais
4. **Especulação**: Permite execução além de desvios

## Limitações Conhecidas

1. **Memória**: Não detecta hazards de memória (assumindo cache perfeito)
2. **Desvios**: Preditor simples (2-bit local)
3. **Labels**: Simplificado para fins educacionais
4. **Exceções**: Não implementadas
5. **Cache**: Não simulado (latências fixas)

## Extensões Possíveis

1. **Preditor mais sofisticado**: Branch Target Buffer, gshare
2. **Multiple issue**: Despachar múltiplas instruções por ciclo
3. **Simulação de cache**: L1, L2, miss penalties
4. **Mais instruções MIPS**: Instruções de ponto flutuante
5. **Detecção de hazards de memória**: Store-to-load forwarding
6. **Visualização de timeline**: Gantt chart de execução

## Testando o Simulador

Execute os testes unitários:

```bash
python -m unittest tests/test_simulator.py
```

Testes cobrem:
- Parse de instruções
- Execução básica
- Dependências de dados
- Operações de memória
- Métricas de desempenho
- ROB e commit em ordem
