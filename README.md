# Simulador do Algoritmo de Tomasulo

<div align="center">

**Simulador educacional do algoritmo de Tomasulo com suporte a instruções MIPS, buffer de reordenamento (ROB) e especulação de desvios condicionais.**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Características

- ✅ **Algoritmo de Tomasulo Completo**: Implementação fiel com Reservation Stations e Register Renaming
- ✅ **Buffer de Reordenamento (ROB)**: Garante commit em ordem e suporta execução especulativa
- ✅ **Especulação de Desvios**: Preditor de 2 bits com flush automático em mispredictions
- ✅ **Instruções MIPS**: ADD, SUB, MUL, DIV, ADDI, LW, SW, BEQ, BNE, J
- ✅ **Interface Gráfica Educacional**: Visualização clara de todos os componentes
- ✅ **Execução Passo a Passo**: Ideal para aprendizado e debugging
- ✅ **Métricas Detalhadas**: IPC, ciclos de bolha, taxa de acerto de desvios
- ✅ **Exemplos Educacionais**: Programas MIPS demonstrativos

## 🚀 Início Rápido

### Instalação

```bash
# Clone o repositório
git clone https://github.com/giusfds/Tomasulo-Algorithm.git
cd Tomasulo-Algorithm

# Instale as dependências
pip install -r requirements.txt
```

### Execução

**Interface Gráfica:**
```bash
python main.py
```

**Demonstração em Terminal:**
```bash
python demo.py
```

**Testes:**
```bash
python -m unittest tests/test_simulator.py
```

## 🎯 Como Usar

### 1. Escrever/Carregar Código MIPS

Digite seu código no editor ou carregue um dos exemplos:

```mips
# Exemplo simples
ADDI R1, R0, 10    # R1 = 10
ADDI R2, R0, 20    # R2 = 20
ADD R3, R1, R2     # R3 = R1 + R2 = 30
MUL R4, R3, R2     # R4 = R3 * R2 = 600
```

### 2. Configurar o Simulador

- **Add RS**: Reservation Stations para ADD/SUB (padrão: 3)
- **Mult RS**: Reservation Stations para MUL/DIV (padrão: 2)
- **ROB Size**: Tamanho do Reorder Buffer (padrão: 16)

### 3. Executar

- **Carregar Programa**: Faz parse e carrega no simulador
- **Próximo Ciclo**: Executa um ciclo (modo educacional)
- **Executar Tudo**: Executa até completar
- **Execução Automática**: Executa com pausas entre ciclos

### 4. Visualizar

A interface mostra em tempo real:
- **Instruções**: Estágio e ciclos de cada instrução
- **Reservation Stations**: Estado de cada RS
- **Reorder Buffer**: Entradas do ROB
- **Registradores**: Valores atuais
- **Métricas**: IPC, bolhas, acertos de desvio

## 📊 Entendendo os Componentes

### Reservation Stations
Buffers que armazenam instruções aguardando execução:
- **Vj, Vk**: Valores dos operandos (quando disponíveis)
- **Qj, Qk**: ROB entries que produzirão os valores (dependências)
- **Dest**: ROB entry de destino

### Reorder Buffer (ROB)
Permite execução fora de ordem com commit em ordem:
- **(H)**: HEAD - próxima instrução para commit
- **(T)**: TAIL - próxima posição livre
- **Ready**: Indica se o resultado está pronto

### Métricas

- **IPC**: Instructions Per Cycle - eficiência da execução
- **Ciclos de Bolha**: Ciclos onde ROB head não pode fazer commit
- **Taxa de Acerto**: Precisão do preditor de desvios

## 📁 Estrutura do Projeto

```
Tomasulo-Algorithm/
├── src/
│   ├── core/
│   │   ├── structures.py      # Estruturas de dados (ROB, RS, etc.)
│   │   └── simulator.py       # Simulador principal
│   ├── mips/
│   │   └── parser.py          # Parser de instruções MIPS
│   └── gui/
│       └── main_window.py     # Interface gráfica
├── examples/                  # Programas MIPS de exemplo
│   ├── example1_basic.asm
│   ├── example2_loop.asm
│   ├── example3_memory.asm
│   ├── example4_hazards.asm
│   ├── example5_parallelism.asm
│   ├── example6_complete.asm
│   └── example7_branch_loop.asm
├── tests/                     # Testes unitários
│   └── test_simulator.py
├── docs/                      # Documentação
│   ├── USER_GUIDE.md         # Guia do usuário
│   └── TECHNICAL.md          # Documentação técnica
├── main.py                    # Entrada principal (GUI)
├── demo.py                    # Demonstração em terminal
└── requirements.txt           # Dependências
```

## 💡 Exemplos de Código

### Exemplo 1: Hazards de Dados
```mips
ADDI R1, R0, 5
ADD R2, R1, R1     # RAW em R1
MUL R3, R2, R1     # RAW em R2 e R1
```

### Exemplo 2: Paralelismo
```mips
ADDI R1, R0, 10    # Independente
ADDI R2, R0, 20    # Independente
ADD R3, R1, R2     # Usa R1, R2
MUL R4, R1, R2     # Pode executar em paralelo
```

### Exemplo 3: Loop com Desvio
```mips
ADDI R1, R0, 0
loop:
ADDI R1, R1, 1
BEQ R1, R2, end
J loop
end:
```

## 🔬 Conceitos Implementados

### 1. Execução Fora de Ordem
Instruções executam assim que seus operandos estão prontos, independente da ordem do programa.

### 2. Register Renaming
Através do ROB, elimina hazards WAR (Write After Read) e WAW (Write After Write).

### 3. Especulação de Desvios
- Preditor de 2 bits prediz se desvio será tomado
- Instruções após desvio são marcadas como especulativas
- Flush automático em caso de misprediction

### 4. Commit em Ordem
Apesar da execução fora de ordem, commit é sempre sequencial para manter semântica correta.

## 📈 Métricas Calculadas

| Métrica | Descrição | Fórmula |
|---------|-----------|---------|
| **IPC** | Instruções por ciclo | `completed / cycles` |
| **Ciclos de Bolha** | Ciclos desperdiçados | Quando ROB head não pode fazer commit |
| **Taxa de Acerto** | Precisão do preditor | `corretas / total_predições` |

## 🎓 Uso Educacional

Este simulador foi projetado para fins didáticos:

1. **Visualização Clara**: Todos os componentes visíveis
2. **Execução Passo a Passo**: Entenda cada ciclo
3. **Exemplos Variados**: Diferentes cenários de hazards
4. **Métricas Detalhadas**: Análise de desempenho

## 📚 Documentação
