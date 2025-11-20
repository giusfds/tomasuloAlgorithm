"""
Demonstração em linha de comando do simulador de Tomasulo
Útil para testes rápidos sem GUI
"""
from src.core.simulator import TomasuloSimulator
from src.mips.parser import MIPSParser


def print_separator():
    print("=" * 80)


def print_instruction_table(simulator):
    """Imprime tabela de instruções"""
    print("\nInstruções:")
    print("-" * 80)
    print(f"{'PC':<4} {'Instrução':<25} {'Issue':<6} {'Exec':<6} {'Write':<6} {'Commit':<6} {'Estágio':<15}")
    print("-" * 80)
    
    for inst in simulator.instructions:
        print(f"{inst.pc:<4} {str(inst):<25} "
              f"{inst.issue_cycle or '-':<6} "
              f"{inst.exec_start_cycle or '-':<6} "
              f"{inst.write_cycle or '-':<6} "
              f"{inst.commit_cycle or '-':<6} "
              f"{inst.stage.value:<15}")


def print_rs_table(simulator):
    """Imprime tabela de reservation stations"""
    print("\nReservation Stations:")
    print("-" * 80)
    
    all_rs = simulator.add_rs + simulator.mul_rs + simulator.load_rs + simulator.store_rs
    
    for rs in all_rs:
        if rs.busy:
            print(f"{rs.name}: {rs.op.value if rs.op else '?'} "
                  f"Vj={rs.vj} Vk={rs.vk} "
                  f"Qj={f'ROB{rs.qj}' if rs.qj is not None else '-'} "
                  f"Qk={f'ROB{rs.qk}' if rs.qk is not None else '-'} "
                  f"Dest=ROB{rs.dest}")


def print_rob_table(simulator):
    """Imprime tabela do ROB"""
    print("\nReorder Buffer:")
    print("-" * 80)
    
    for i, entry in enumerate(simulator.rob):
        if entry.busy:
            marker = ""
            if i == simulator.rob_head:
                marker = "(HEAD)"
            if i == simulator.rob_tail:
                marker += "(TAIL)"
                
            spec = " [SPEC]" if entry.speculative else ""
            print(f"ROB{i}{marker}: {entry.state:<8} "
                  f"Inst={str(entry.instruction) if entry.instruction else '?':<25} "
                  f"Dest={entry.dest or '-':<8} "
                  f"Value={entry.value if entry.value is not None else '-':<8} "
                  f"Ready={entry.ready}{spec}")


def print_registers(simulator):
    """Imprime registradores"""
    print("\nRegistradores:")
    print("-" * 80)
    
    # Mostrar apenas registradores não-zero
    non_zero = {k: v for k, v in simulator.registers.items() if v != 0 or k == 'R0'}
    
    for i in range(0, len(non_zero), 4):
        regs = list(non_zero.items())[i:i+4]
        line = "  ".join([f"{k}={v:4}" for k, v in regs])
        print(line)


def print_metrics(simulator):
    """Imprime métricas"""
    print("\nMétricas de Desempenho:")
    print("-" * 80)
    metrics = simulator.metrics
    bp = simulator.branch_predictor
    
    print(f"Ciclo Atual:              {simulator.current_cycle}")
    print(f"Instruções Despachadas:   {metrics.instructions_issued}")
    print(f"Instruções Completadas:   {metrics.instructions_completed}")
    print(f"IPC:                      {metrics.get_ipc():.3f}")
    print(f"Ciclos de Bolha:          {metrics.bubble_cycles}")
    print(f"Ciclos de Stall:          {metrics.stall_cycles}")
    print(f"Predições de Desvio:      {bp.predictions}")
    print(f"Predições Corretas:       {bp.correct_predictions}")
    print(f"Taxa de Acerto:           {bp.get_accuracy()*100:.1f}%")
    print(f"Mispredictions:           {metrics.branch_mispredictions}")


def run_demo(program_text, step_by_step=False, config=None):
    """Executa uma demonstração"""
    print_separator()
    print("SIMULADOR DE TOMASULO - DEMONSTRAÇÃO")
    print_separator()
    
    # Parse do programa
    parser = MIPSParser()
    instructions = parser.parse_program(program_text)
    
    print(f"\nPrograma carregado: {len(instructions)} instruções")
    
    # Criar simulador
    if config is None:
        config = {}
    simulator = TomasuloSimulator(config)
    simulator.load_program(instructions)
    
    if step_by_step:
        # Execução passo a passo
        cycle = 0
        while not simulator.finished and cycle < 100:
            print_separator()
            print(f"CICLO {simulator.current_cycle + 1}")
            print_separator()
            
            simulator.step()
            
            print_instruction_table(simulator)
            print_rs_table(simulator)
            print_rob_table(simulator)
            print_registers(simulator)
            print_metrics(simulator)
            
            if not simulator.finished:
                input("\nPressione ENTER para próximo ciclo...")
            
            cycle += 1
    else:
        # Execução completa
        simulator.run_until_complete()
        
    # Resultados finais
    print_separator()
    print("RESULTADOS FINAIS")
    print_separator()
    
    print_instruction_table(simulator)
    print_registers(simulator)
    print_metrics(simulator)
    
    return simulator


def demo1_basic():
    """Demonstração 1: Operações básicas"""
    program = """
    # Operações aritméticas básicas
    ADDI R1, R0, 10
    ADDI R2, R0, 20
    ADD R3, R1, R2
    SUB R4, R3, R1
    MUL R5, R3, R2
    """
    
    print("\n### DEMO 1: Operações Básicas ###\n")
    run_demo(program)


def demo2_dependencies():
    """Demonstração 2: Dependências de dados"""
    program = """
    # Cadeia de dependências
    ADDI R1, R0, 5
    ADD R2, R1, R1
    MUL R3, R2, R1
    DIV R4, R3, R2
    """
    
    print("\n### DEMO 2: Dependências de Dados ###\n")
    run_demo(program)


def demo3_parallelism():
    """Demonstração 3: Paralelismo"""
    program = """
    # Instruções independentes (paralelismo)
    ADDI R1, R0, 10
    ADDI R2, R0, 20
    ADDI R3, R0, 30
    ADDI R4, R0, 40
    ADD R5, R1, R2
    MUL R6, R3, R4
    """
    
    print("\n### DEMO 3: Paralelismo ###\n")
    run_demo(program)


def demo4_memory():
    """Demonstração 4: Operações de memória"""
    program = """
    # Load e Store
    ADDI R1, R0, 100
    ADDI R2, R0, 42
    SW R2, 0(R1)
    SW R2, 4(R1)
    LW R3, 0(R1)
    LW R4, 4(R1)
    ADD R5, R3, R4
    """
    
    print("\n### DEMO 4: Operações de Memória ###\n")
    run_demo(program)


def main():
    """Função principal"""
    print("\n" + "="*80)
    print(" SIMULADOR DE TOMASULO - DEMONSTRAÇÕES")
    print("="*80)
    
    demos = [
        ("1. Operações Básicas", demo1_basic),
        ("2. Dependências de Dados", demo2_dependencies),
        ("3. Paralelismo", demo3_parallelism),
        ("4. Operações de Memória", demo4_memory),
    ]
    
    while True:
        print("\nEscolha uma demonstração:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"{i}. {name}")
        print("0. Sair")
        
        try:
            choice = int(input("\nOpção: "))
            if choice == 0:
                break
            elif 1 <= choice <= len(demos):
                demos[choice-1][1]()
            else:
                print("Opção inválida!")
        except ValueError:
            print("Por favor, digite um número!")
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
    
    print("\nObrigado por usar o simulador!")


if __name__ == '__main__':
    main()
