# Exemplo 4: Hazards RAW, WAR e WAW
# Demonstra diferentes tipos de hazards

# RAW (Read After Write) - dependência verdadeira
ADD R1, R2, R3     # R1 = R2 + R3
SUB R4, R1, R5     # R4 = R1 - R5 (RAW em R1)

# WAR (Write After Read) - evitado por renomeamento
ADD R6, R7, R8     # R6 = R7 + R8
MUL R7, R9, R10    # R7 = R9 * R10 (WAR em R7, mas ROB resolve)

# WAW (Write After Write) - evitado por ROB
ADDI R11, R0, 10   # R11 = 10
ADDI R11, R0, 20   # R11 = 20 (WAW em R11, ROB mantém ordem)

# Múltiplas dependências
ADD R12, R1, R4    # Depende de R1 e R4
MUL R13, R12, R6   # Depende de R12 e R6
DIV R14, R13, R11  # Depende de R13 e R11
