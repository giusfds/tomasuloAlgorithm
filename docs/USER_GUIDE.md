# Guia do Usuário - Simulador de Tomasulo

## Introdução

Este simulador implementa o algoritmo de Tomasulo, uma técnica de execução fora de ordem que permite a execução paralela de instruções enquanto resolve dependências de dados automaticamente.

## Características Principais

### 1. Algoritmo de Tomasulo
- **Reservation Stations**: Buffers que armazenam instruções aguardando execução
- **Reorder Buffer (ROB)**: Garante commit em ordem e suporta especulação
- **Register Renaming**: Elimina hazards WAR e WAW automaticamente
- **Execução Fora de Ordem**: Instruções executam assim que seus operandos estão prontos

### 2. Especulação de Desvios
- Preditor de desvios de 2 bits
- Execução especulativa após desvios
- Flush automático em caso de misprediction

### 3. Métricas de Desempenho
- **IPC** (Instructions Per Cycle): Mede eficiência
- **Ciclos de Bolha**: Ciclos onde nenhuma instrução faz commit
- **Ciclos de Stall**: Ciclos onde nenhuma instrução é despachada
- **Taxa de Acerto de Desvios**: Precisão do preditor

## Como Usar

### Passo 1: Instalação

```bash
pip install -r requirements.txt
```

### Passo 2: Executar o Simulador

```bash
python main.py
```

### Passo 3: Carregar um Programa

1. Digite código MIPS no editor à esquerda, ou
2. Clique em "Carregar Arquivo" para abrir um arquivo .asm, ou
3. Clique em "Carregar Exemplo" para um programa demonstrativo

### Passo 4: Configurar o Simulador

Ajuste as configurações:
- **Add RS**: Número de Reservation Stations para ADD/SUB
- **Mult RS**: Número de Reservation Stations para MUL/DIV
- **ROB Size**: Tamanho do Reorder Buffer

### Passo 5: Executar

- **Carregar Programa**: Parse e carrega o programa
- **Próximo Ciclo**: Executa um ciclo por vez (modo passo a passo)
- **Executar Tudo**: Executa até o final
- **Execução Automática**: Executa automaticamente com pausa entre ciclos
- **Resetar**: Volta ao estado inicial

## Entendendo a Interface

### Tabela de Instruções
Mostra todas as instruções com seus ciclos de:
- **Issue**: Quando foi despachada
- **Exec**: Quando começou/terminou execução
- **Write**: Quando escreveu resultado
- **Commit**: Quando fez commit

Cores indicam o estágio atual:
- 🔲 Cinza: Aguardando
- 🔵 Azul: Despachada
- 🟡 Amarelo: Executando
- 🟢 Verde claro: Escrevendo resultado
- 🟢 Verde: Commit completo

### Reservation Stations
Mostra o estado de cada RS:
- **Busy**: Se está ocupada
- **Op**: Operação sendo executada
- **Vj, Vk**: Valores dos operandos (quando prontos)
- **Qj, Qk**: ROB entries que produzirão os valores (dependências)
- **Dest**: ROB entry de destino

### Reorder Buffer (ROB)
Mostra todas as entradas do ROB:
- **(H)**: Marca a HEAD (próxima para commit)
- **(T)**: Marca a TAIL (próxima livre)
- **Estado**: Issue, Execute, Write, ou Commit
- **Ready**: Se o valor está pronto

Cores:
- 🟡 Amarelo: HEAD (próxima para commit)
- 🟠 Laranja: Especulativa
- 🔵 Azul: Ativa
- ⚪ Cinza: Livre

### Registradores
Mostra os valores atuais dos registradores R0-R15.

### Métricas
Estatísticas em tempo real:
- Ciclos executados
- IPC atual
- Bolhas e stalls
- Precisão do preditor de desvios

## Exemplos de Código MIPS

### Exemplo 1: Operações Básicas
```mips
ADDI R1, R0, 10
ADDI R2, R0, 20
ADD R3, R1, R2
```

### Exemplo 2: Dependências
```mips
ADDI R1, R0, 5
ADD R2, R1, R1    # Depende de R1
MUL R3, R2, R1    # Depende de R2 e R1
```

### Exemplo 3: Memória
```mips
ADDI R1, R0, 100
ADDI R2, R0, 42
SW R2, 0(R1)      # Armazena 42 em Mem[100]
LW R3, 0(R1)      # Carrega de Mem[100]
```

### Exemplo 4: Desvios
```mips
ADDI R1, R0, 0
loop:
ADDI R1, R1, 1
ADDI R2, R0, 10
BEQ R1, R2, end
J loop
end:
ADDI R3, R1, 0
```

## Conceitos Importantes

### Hazards de Dados
- **RAW** (Read After Write): Dependência verdadeira - resolvida por forwarding
- **WAR** (Write After Read): Eliminada por register renaming
- **WAW** (Write After Write): Eliminada por ROB

### Execução Fora de Ordem
Instruções executam assim que:
1. Uma RS estiver livre
2. Todos os operandos estiverem prontos
3. A unidade funcional estiver disponível

### Commit em Ordem
Mesmo executando fora de ordem, o commit é sempre em ordem para:
- Manter semântica correta
- Permitir exceções precisas
- Facilitar especulação

### Especulação
Após um desvio condicional:
1. Preditor faz uma predição
2. Instruções seguintes são marcadas como especulativas
3. Se predição estiver correta: commit normal
4. Se predição estiver errada: flush de instruções especulativas

## Latências Padrão

- ADD/SUB: 2 ciclos
- ADDI: 2 ciclos
- MUL: 10 ciclos
- DIV: 20 ciclos
- LW: 3 ciclos
- SW: 3 ciclos
- BEQ/BNE: 1 ciclo

## Troubleshooting

### Programa não carrega
- Verifique sintaxe MIPS
- Cada instrução deve estar em uma linha
- Use comentários com #

### Simulação não progride
- Verifique se há RS suficientes
- Verifique se ROB não está cheio
- Instruções podem estar aguardando dependências

### Resultados incorretos
- Verifique hazards de memória (loads/stores)
- Verifique se registradores foram inicializados
- R0 sempre contém 0

## Exercícios Sugeridos

1. **Paralelismo**: Crie programas com instruções independentes e observe IPC
2. **Dependências**: Teste diferentes padrões de dependências
3. **Desvios**: Compare desempenho com/sem desvios
4. **Configuração**: Varie número de RS e observe impacto
5. **Memória**: Explore hazards de load/store

## Referências

- Tomasulo, R. M. (1967). "An Efficient Algorithm for Exploiting Multiple Arithmetic Units"
- Hennessy & Patterson. "Computer Architecture: A Quantitative Approach"
