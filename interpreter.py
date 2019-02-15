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
    'n' : 0b0,  #NEGATION FLAG
    'c' : 0b0,  #CARRY FLAG
    'v' : 0b0,  #OVERFLOW FLAG
    }


REGISTERS = { "$" + str(hex(i))[-1].upper() : 0b00000000 for i in range(0x10)}

PC = 0x0    #Program Counter
IR = ()     #Instrction Register (16-bits)

#RAM
MAR = [] #Master Address Register (0x0000-0xFFFF)
MDR = [] #Master Data Register (0x0000-0xFFFF)


def parse_instruction(ins) -> tuple:
    """Takes an instruction as a string and returns a tuple with the correspondant binary instruction."""
    instructions = ins.replace(' ', '')
    instructions = instructions.split(',')
    try:
        #Checks if the given instruction is in the Instruction Set
        if(instructions[0] in INSTRUCTION_SET):
           instructions[0] = INSTRUCTION_SET[instructions[0]]
        else:
            raise InvalidInstructionError
        #Checks if the instruction is an Immediate Instruction
        if(instructions[0] < 0b100):
            #Raise an exception if the instruction contains an invalid amount of arguments
            if(len(instructions) != 3):
                raise InvalidArgumentError
            #Raises an exception fi the third argument is not an 8-bit signed immediate
            elif(len(instructions[2]) != 3):
                raise InvalidArgumentError
            else:
                argument = instructions[2]
                instructions[2] = '$' + argument[1]
                instructions.append('$' + argument[2])

        #Raise an exception if the instruction contains an invalid amount of arguments       
        elif(len(instructions) != 4):
                raise InvalidArgumentError
            
        #Converts each argument into its corresponding binary form
        for i in range(1, len(instructions)):
            #Checks if the argument is valid
            if(instructions[i][0] != '$'):
                raise InvalidInstructionError
            else:
                instructions[i] = bin(int(instructions[i][1], 16))
                
        instructions[0] = bin(instructions[0])
        return tuple(instructions)
    
    except InvalidInstructionError:
        print("\'{}\' instruction not recognized".format(instructions[0]))
    except InvalidArgumentError:
        print("The instruction contains invalid arguments")

def load_instruction(ins):
    """Loads a given instruction into RAM"""
    #Raises an exception if there aren't any available registers in RAM
    if(PC > 0xFFFF):
        raise MemoryOverflowException
    MAR.append((ins[0], ins[1]))
    MDR.append((ins[2], ins[3]))

def fetch_instruction():
    """Fetches the last instruction from memory"""
    global PC
    global IR
    IR = MAR[PC] + MDR[PC]
    PC += 1

def mux(s, value = None):
    """16 to 1 multiplexer"""
    s = s[2:]
    s = [0b1111 * int(i) for i in s[::-1]]
        
    #Bitwise negation
    neg = lambda i : 0 if i == 0b1111 else 0b1111
    
    #2 to 1 multiplexer
    mux_2_1 = lambda a, b, sn: (a & neg(sn)) | (b & sn)
    
    z = list(range(0x0, 0x10))   #Inputs
    index = 0 
    while(len(z) > 1):
        prev = z.copy()
        z = [mux_2_1(prev[i], prev[i+1], s[index]) for i in range(0, len(prev), 2)]
        index += 1

    address = '$' + hex(z[0])[-1]
    if(value):
        global REGISTERS
        if(address != '$0'):
            REGISTERS[address] = value
    else:
        return REGISTERS[address]     
        

class MemoryOverflowException(Exception):
    pass
        
class InvalidInstructionError(Exception):
    pass

class InvalidArgumentError(Exception):
    pass
