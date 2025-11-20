# Exemplo 7: Programa com Desvio e Loop
# Calcula soma de 1 até N usando loop

# Inicialização
ADDI R1, R0, 1     # R1 = 1 (contador inicial)
ADDI R2, R0, 10    # R2 = 10 (N - limite)
ADDI R3, R0, 0     # R3 = 0 (soma acumulada)

# Loop principal
loop:
ADD R3, R3, R1     # soma += contador
ADDI R1, R1, 1     # contador++
BNE R1, R2, loop   # Se contador != N, volta ao loop

# Finalização
ADDI R4, R3, 0     # R4 = soma (resultado final)
# Resultado esperado: R4 = 45 (soma de 1 a 9)
