"""
Testes unitários para o simulador de Tomasulo
"""
import unittest
from src.core.simulator import TomasuloSimulator
from src.core.structures import InstructionType, Instruction
from src.mips.parser import MIPSParser


class TestMIPSParser(unittest.TestCase):
    """Testes para o parser MIPS"""
    
    def setUp(self):
        self.parser = MIPSParser()
        
    def test_parse_add(self):
        """Testa parse de ADD"""
        inst = self.parser.parse_instruction("ADD R1, R2, R3", 0)
        self.assertEqual(inst.type, InstructionType.ADD)
        self.assertEqual(inst.dest, "R1")
        self.assertEqual(inst.src1, "R2")
        self.assertEqual(inst.src2, "R3")
        
    def test_parse_addi(self):
        """Testa parse de ADDI"""
        inst = self.parser.parse_instruction("ADDI R1, R2, 10", 0)
        self.assertEqual(inst.type, InstructionType.ADDI)
        self.assertEqual(inst.dest, "R1")
        self.assertEqual(inst.src1, "R2")
        self.assertEqual(inst.immediate, 10)
        
    def test_parse_lw(self):
        """Testa parse de LW"""
        inst = self.parser.parse_instruction("LW R1, 4(R2)", 0)
        self.assertEqual(inst.type, InstructionType.LW)
        self.assertEqual(inst.dest, "R1")
        self.assertEqual(inst.src1, "R2")
        self.assertEqual(inst.offset, 4)
        
    def test_parse_program(self):
        """Testa parse de programa completo"""
        program = """
        ADDI R1, R0, 10
        ADDI R2, R0, 20
        ADD R3, R1, R2
        """
        instructions = self.parser.parse_program(program)
        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[0].type, InstructionType.ADDI)
        self.assertEqual(instructions[2].type, InstructionType.ADD)


class TestTomasuloSimulator(unittest.TestCase):
    """Testes para o simulador de Tomasulo"""
    
    def setUp(self):
        self.simulator = TomasuloSimulator()
        self.parser = MIPSParser()
        
    def test_simple_add(self):
        """Testa execução de ADD simples"""
        program = """
        ADDI R1, R0, 10
        ADDI R2, R0, 20
        ADD R3, R1, R2
        """
        instructions = self.parser.parse_program(program)
        self.simulator.load_program(instructions)
        self.simulator.run_until_complete()
        
        self.assertEqual(self.simulator.registers['R1'], 10)
        self.assertEqual(self.simulator.registers['R2'], 20)
        self.assertEqual(self.simulator.registers['R3'], 30)
        
    def test_dependencies(self):
        """Testa hazards de dados"""
        program = """
        ADDI R1, R0, 5
        ADD R2, R1, R1
        MUL R3, R2, R1
        """
        instructions = self.parser.parse_program(program)
        self.simulator.load_program(instructions)
        self.simulator.run_until_complete()
        
        self.assertEqual(self.simulator.registers['R1'], 5)
        self.assertEqual(self.simulator.registers['R2'], 10)
        self.assertEqual(self.simulator.registers['R3'], 50)
        
    def test_memory_operations(self):
        """Testa operações de memória"""
        program = """
        ADDI R1, R0, 100
        ADDI R2, R0, 42
        SW R2, 0(R1)
        LW R3, 0(R1)
        """
        instructions = self.parser.parse_program(program)
        self.simulator.load_program(instructions)
        self.simulator.run_until_complete()
        
        self.assertEqual(self.simulator.registers['R3'], 42)
        self.assertEqual(self.simulator.memory[100], 42)
        
    def test_ipc_calculation(self):
        """Testa cálculo de IPC"""
        program = """
        ADDI R1, R0, 1
        ADDI R2, R0, 2
        ADDI R3, R0, 3
        """
        instructions = self.parser.parse_program(program)
        self.simulator.load_program(instructions)
        self.simulator.run_until_complete()
        
        ipc = self.simulator.metrics.get_ipc()
        self.assertGreater(ipc, 0)
        self.assertEqual(self.simulator.metrics.instructions_completed, 3)


class TestReservationStations(unittest.TestCase):
    """Testes para Reservation Stations"""
    
    def setUp(self):
        self.simulator = TomasuloSimulator()
        
    def test_rs_allocation(self):
        """Testa alocação de RS"""
        program = """
        ADDI R1, R0, 1
        ADDI R2, R0, 2
        ADDI R3, R0, 3
        """
        parser = MIPSParser()
        instructions = parser.parse_program(program)
        self.simulator.load_program(instructions)
        
        # Executar alguns ciclos
        for _ in range(5):
            self.simulator.step()
            
        # Verificar que instruções foram despachadas
        self.assertGreater(self.simulator.metrics.instructions_issued, 0)


class TestROB(unittest.TestCase):
    """Testes para Reorder Buffer"""
    
    def setUp(self):
        self.simulator = TomasuloSimulator({'rob_size': 8})
        
    def test_rob_commit_order(self):
        """Testa commit em ordem no ROB"""
        program = """
        ADDI R1, R0, 1
        MUL R2, R1, R1
        ADDI R3, R0, 3
        """
        parser = MIPSParser()
        instructions = parser.parse_program(program)
        self.simulator.load_program(instructions)
        self.simulator.run_until_complete()
        
        # Verificar que todas as instruções foram completadas
        self.assertEqual(self.simulator.metrics.instructions_completed, 3)
        
        # Verificar ordem de commit
        self.assertIsNotNone(instructions[0].commit_cycle)
        self.assertIsNotNone(instructions[1].commit_cycle)
        self.assertIsNotNone(instructions[2].commit_cycle)
        
        # Commit deve ser em ordem
        self.assertLess(instructions[0].commit_cycle, instructions[1].commit_cycle)
        self.assertLess(instructions[1].commit_cycle, instructions[2].commit_cycle)


if __name__ == '__main__':
    unittest.main()
