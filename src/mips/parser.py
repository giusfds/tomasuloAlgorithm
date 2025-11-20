"""
Parser de instruções MIPS
"""
from typing import List, Dict
from src.core.structures import Instruction, InstructionType


class MIPSParser:
    """Parser para instruções MIPS"""
    
    def __init__(self):
        self.labels = {}  # label -> PC
        
    def parse_program(self, program_text: str) -> List[Instruction]:
        """Parse um programa MIPS completo"""
        lines = program_text.strip().split('\n')
        instructions = []
        pc = 0
        
        # Primeiro passo: encontrar labels
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if ':' in line:
                label = line.split(':')[0].strip()
                self.labels[label] = pc
                line = line.split(':', 1)[1].strip()
                if not line:
                    continue
                    
            # Contar instrução válida
            if self._is_valid_instruction(line):
                pc += 1
        
        # Segundo passo: parse instruções
        pc = 0
        for line in lines:
            line = line.strip()
            
            # Ignorar comentários e linhas vazias
            if not line or line.startswith('#'):
                continue
                
            # Remover labels
            if ':' in line:
                line = line.split(':', 1)[1].strip()
                if not line:
                    continue
            
            # Remover comentários inline
            if '#' in line:
                line = line.split('#')[0].strip()
                
            inst = self.parse_instruction(line, pc)
            if inst:
                instructions.append(inst)
                pc += 1
                
        return instructions
    
    def _is_valid_instruction(self, line: str) -> bool:
        """Verifica se a linha contém uma instrução válida"""
        if '#' in line:
            line = line.split('#')[0].strip()
        return bool(line)
    
    def parse_instruction(self, line: str, pc: int = 0) -> Instruction:
        """Parse uma única instrução MIPS"""
        parts = line.replace(',', ' ').split()
        if not parts:
            return None
            
        op = parts[0].upper()
        
        try:
            if op in ['ADD', 'SUB', 'MUL', 'DIV']:
                # Formato: OP rd, rs, rt
                inst_type = InstructionType[op]
                return Instruction(inst_type, parts[1], parts[2], parts[3], pc=pc)
                
            elif op == 'ADDI':
                # Formato: ADDI rt, rs, imm
                return Instruction(InstructionType.ADDI, parts[1], parts[2], 
                                 immediate=int(parts[3]), pc=pc)
                
            elif op == 'LW':
                # Formato: LW rt, offset(rs)
                offset_parts = parts[2].split('(')
                offset = int(offset_parts[0])
                base = offset_parts[1].rstrip(')')
                return Instruction(InstructionType.LW, parts[1], base, 
                                 offset=offset, pc=pc)
                
            elif op == 'SW':
                # Formato: SW rt, offset(rs)
                offset_parts = parts[2].split('(')
                offset = int(offset_parts[0])
                base = offset_parts[1].rstrip(')')
                return Instruction(InstructionType.SW, None, base, parts[1],
                                 offset=offset, pc=pc)
                
            elif op in ['BEQ', 'BNE']:
                # Formato: BEQ rs, rt, label
                inst_type = InstructionType[op]
                return Instruction(inst_type, None, parts[1], parts[2], 
                                 label=parts[3], pc=pc)
                
            elif op == 'J':
                # Formato: J label
                return Instruction(InstructionType.J, label=parts[1], pc=pc)
                
            elif op == 'NOP':
                return Instruction(InstructionType.NOP, pc=pc)
                
        except (IndexError, ValueError, KeyError) as e:
            print(f"Erro ao fazer parse da instrução '{line}': {e}")
            return None
            
        return None
        
    def get_label_pc(self, label: str) -> int:
        """Retorna o PC de um label"""
        return self.labels.get(label, -1)
