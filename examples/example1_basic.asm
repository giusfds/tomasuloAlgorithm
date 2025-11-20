# Exemplo 1: Operações Aritméticas Básicas
# Demonstra hazards de dados e execução fora de ordem

ADDI R1, R0, 10    # R1 = 10
ADDI R2, R0, 20    # R2 = 20
ADD R3, R1, R2     # R3 = R1 + R2 = 30 (depende de R1 e R2)
SUB R4, R3, R1     # R4 = R3 - R1 = 20 (depende de R3)
MUL R5, R3, R2     # R5 = R3 * R2 = 600 (depende de R3)
ADDI R6, R0, 2     # R6 = 2 (pode executar em paralelo)
DIV R7, R5, R6     # R7 = R5 / R6 = 300 (depende de R5 e R6)
