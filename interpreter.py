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

#Memory
MAR = [] #Master Address Register (0x0000-0xFFFF)
MDR = [] #Master Data Register (0x0000-0xFFFF)

neg = lambda i : 0 if i == 0b1111 else 0b1111       #Bitwise negation
mux_2_1 = lambda a, b, sn: (a & neg(sn)) | (b & sn) #2 to 1 multiplexer


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
                
        instructions[0] = instructions[0]
        return tuple(instructions)
    
    except InvalidInstructionError:
        print("\'{}\' instruction not recognized".format(instructions[0]))
    except InvalidArgumentError:
        print("The instruction contains invalid arguments")

def load_instruction(ins):
    """Loads a given instruction into memory"""
    #Raises an exception if there aren't any available registers in RAM
    if(PC > 0xFFFF):
        raise MemoryOverflowException
    MAR.append((ins[0], ins[1]))
    MDR.append((ins[2], ins[3]))

def fetch_instruction():
    """Fetches the last instruction from memory"""
    global PC
    global IR
    #Stores the data from the MAR and the MDR into the IR
    IR = MAR[PC] + MDR[PC]
    PC += 1

def mux(s, value = None):
    """16 to 1 multiplexer

    If no value has been specified, it returns the value stored at the given register,
    else, it stores the value to the register.
    """
    s = s[2:]
    s = [0b1111 * int(i) for i in s[::-1]]
    
    z = list(range(0x0, 0x10))   #Inputs (0x0-0xF)
    index = 0 
    while(len(z) > 1):
        prev = z.copy()
        z = [mux_2_1(prev[i], prev[i+1], s[index]) for i in range(0, len(prev), 2)]
        index += 1

    address = '$' + hex(z[0])[-1]

    #If a value was passed, access the register at the given address,
    #else, return the register's value
    if(value):
        global REGISTERS
        if(address != '$0'):
            REGISTERS[address] = value
    else:
        return REGISTERS[address]

class Adder():
    """Adds two binary numbers
    """

    @staticmethod
    def __half_adder__(a, b):
        """Takes two input values a, b of type string and returns a tuple
        containing the XOR of the inputs and its carry"""
        return (a ^ b, a & b)   #(sum, carry)

    def __full_adder__(self, a, b, c) -> tuple:
        """Takes three inputs, two adding bits and one carry and performs a binary
        addition."""
        s1, c0 = self.__half_adder__(a, b)
        sum_, c1 = self.__half_adder__(c, s1)
        return (sum_, c0 | c1)

    def add(self, a, b, c = 0):
        result = ''
        carry = c
        length = len(a) - 1
        for i in range(length, -1, -1):
            sum_, carry = self.__full_adder__(int(a[i]), int(b[i]), int(carry))
            result = str(sum_) + result
        return result
        
        
class ALU():
    """Arithmetic Logical Unit handles all of the arithmetic instructions
    """

    def execute_instruction():
        pass

        

class MemoryOverflowException(Exception):
    pass
        
class InvalidInstructionError(Exception):
    pass

class InvalidArgumentError(Exception):
    pass



"""
Effective address: specific location of data in memoroy

Memory Addressing Modes
Load instruction: 1 reg, address
    Data transger: reg <-- MEM[address]

Modes of specifying a memory address:
    -Immediate: address is a constant
    -Pointer: address is contents of a register
    -Base-displacement: [register] + constant
        Uses: local variables, object fields, immediate4, pointer
    -Base-index: [register1] + [register2]
        Uses: array element access, pointer
    -Base-index-disp: [register1] + [register2] + constant
    -Inderect: [MEM[register]]
"""
