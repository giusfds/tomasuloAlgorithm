# Exemplo 2: Loop com Desvio Condicional
# Demonstra especulação de desvios

ADDI R1, R0, 0     # R1 = 0 (contador)
ADDI R2, R0, 10    # R2 = 10 (limite)
ADDI R3, R0, 0     # R3 = 0 (soma acumulada)

loop:
ADD R3, R3, R1     # R3 = R3 + R1 (acumula)
ADDI R1, R1, 1     # R1 = R1 + 1 (incrementa contador)
BEQ R1, R2, end    # Se R1 == R2, vai para end
J loop             # Volta para loop

end:
ADDI R4, R3, 0     # R4 = R3 (resultado final)
