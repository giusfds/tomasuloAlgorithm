# Exemplo 5: Paralelismo de Instruções
# Demonstra execução paralela de instruções independentes

# Grupo 1 - independentes
ADDI R1, R0, 10
ADDI R2, R0, 20
ADDI R3, R0, 30
ADDI R4, R0, 40

# Grupo 2 - operações que podem executar em paralelo
ADD R5, R1, R2     # Usa R1 e R2
MUL R6, R3, R4     # Usa R3 e R4 (pode executar em paralelo com ADD)

# Grupo 3 - cadeia de dependências
ADD R7, R5, R6     # Depende de R5 e R6
SUB R8, R7, R1     # Depende de R7
MUL R9, R8, R2     # Depende de R8

# Grupo 4 - mais operações independentes
ADDI R10, R0, 5
ADDI R11, R0, 15
ADD R12, R10, R11  # Pode executar em paralelo com cadeia anterior
