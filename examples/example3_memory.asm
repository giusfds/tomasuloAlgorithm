# Exemplo 3: Operações de Load/Store
# Demonstra hazards de memória

ADDI R1, R0, 100   # R1 = 100 (endereço base)
ADDI R2, R0, 42    # R2 = 42 (valor a armazenar)
SW R2, 0(R1)       # Mem[100] = 42
SW R2, 4(R1)       # Mem[104] = 42
LW R3, 0(R1)       # R3 = Mem[100] = 42
LW R4, 4(R1)       # R4 = Mem[104] = 42
ADD R5, R3, R4     # R5 = R3 + R4 = 84
