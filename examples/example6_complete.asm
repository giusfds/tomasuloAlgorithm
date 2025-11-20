# Exemplo 6: Teste Completo de Tomasulo
# Demonstra todas as características do simulador

# Seção 1: Paralelismo de instruções independentes
ADDI R1, R0, 10    # Independente
ADDI R2, R0, 20    # Independente
ADDI R3, R0, 30    # Independente
ADD R4, R1, R2     # Depende de R1, R2
MUL R5, R3, R2     # Depende de R3, R2 (pode executar em paralelo com ADD R4)

# Seção 2: Cadeia de dependências
ADD R6, R4, R5     # Depende de R4 e R5
SUB R7, R6, R1     # Depende de R6
MUL R8, R7, R2     # Depende de R7

# Seção 3: Operações de memória
ADDI R10, R0, 200  # Base da memória
SW R4, 0(R10)      # Armazena R4
SW R5, 4(R10)      # Armazena R5
LW R11, 0(R10)     # Carrega valor
LW R12, 4(R10)     # Carrega valor
ADD R13, R11, R12  # Soma valores carregados

# Seção 4: Mais paralelismo
ADDI R14, R0, 5    # Independente de tudo acima
ADDI R15, R0, 15   # Independente de tudo acima
MUL R16, R14, R15  # Usa R14, R15

# Seção 5: WAW e WAR (resolvidos por register renaming)
ADDI R20, R0, 100  # Primeira escrita em R20
ADD R21, R20, R1   # Lê R20
ADDI R20, R0, 200  # WAW - segunda escrita em R20
ADD R22, R21, R20  # Usa novo R20

# Resultado final esperado:
# R1=10, R2=20, R3=30
# R4=30, R5=600
# R6=630, R7=620, R8=12400
# R11=30, R12=600, R13=630
# R14=5, R15=15, R16=75
# R20=200, R21=110, R22=310
