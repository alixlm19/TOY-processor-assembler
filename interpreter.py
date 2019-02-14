INSTRUCTION_SET = {
    "add" : 0b1111,      #|Arithmetic / Logical|
    "sub" : 0b1110,      #|                    |
    "and" : 0b1101,      #|                    |
    "nor" : 0b1100,      #|____________________|

    "l"   : 0b1011,      #|----Load / Store----|
    "lwr" : 0b1010,      #|                    |
    "st"  : 0b1001,      #|                    |
    "stc" : 0b1000,      #|____________________|

    "sru" : 0b0111,      #|Shift/Branch & Link-|
    "srs" : 0b0110,      #|                    |
    "bcl" : 0b0101,      #|                    |
    "sl"  : 0b0100,      #|____________________|

    "lih" : 0b0011,      #|-----Immediate------|
    "lis" : 0b0010,      #|                    |
    "bc"  : 0b0001,      #|                    |
    "sys" : 0b0000,      #|____________________|
    }

FLAGS = {
    'z' : 0b0,  #ZERO FLAG
    'n' : 0b0,  #
    'c' : 0b0,  #CARRY FLAG
    'v' : 0b0,  #
    }

REGISTERS = [[hex(i)] for i in range(16)]

class InstructionError(Exception):
    pass

def parse_instruction(instruction):
    """Takes an instruction as a string and returns to correspondant binary instruction"""
    instructions = instruction.replace(' ', '')
    instructions = instruction.split(',')
    if(len(instructions) != 4):
        raise InstructionError("Instruction contains an invalid amount of arguments")
    instructions[0] = INSTRUCTION_SET[instructions[0]]
        
