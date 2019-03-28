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

REGISTERS = {i:0 for i in range(0x10)}

PC = 0x0    #Program Counter
IR = ()     #Instrction Register (16-bits)

#Memory
MAR = [] #Master Address Register (0x0000-0xFFFF)
MDR = [] #Master Data Register (0x0000-0xFFFF)

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

def negate(d):
        return 1 - d
    
class Inverter():

    def invert(self, d, s):
        return (s & negate(d)) | (d & negate(s))
    
class Two_one_MUX():
    """2 to 1 multiplexer"""
    def select(self, a, b, sn):
        return (a & negate(sn)) | (b & sn)

#FIX THE MULTIPLEXER
class MUX():
    """16 to 1 multiplexer

    If no value has been specified, it returns the value stored at the given register,
    else, it stores the value to the register.
    """
    def __init__(self, data, selector = 2):
        
        #Initialize the 2-1 multiplexers
        self.mux_1 = Two_one_MUX()
        self.mux_2 = Two_one_MUX()
        self.mux_3 = Two_one_MUX()
        self.mux_4 = Two_one_MUX()
        self.mux_5 = Two_one_MUX()
        self.mux_6 = Two_one_MUX()
        self.mux_7 = Two_one_MUX()
        self.mux_8 = Two_one_MUX()
        self.mux_9 = Two_one_MUX()
        self.mux_10 = Two_one_MUX()
        self.mux_11 = Two_one_MUX()
        self.mux_12 = Two_one_MUX()
        self.mux_13 = Two_one_MUX()
        self.mux_14 = Two_one_MUX()
        self.mux_15 = Two_one_MUX()
        self.mux_16 = Two_one_MUX()

    def select(self, s):
        s0, s1, s2, s3 = [int(i) for i in bin(s)[2:]]
        
        out_1 = self.mux_1.select(0, 1, s0)
        out_2 = self.mux_2.select(2, 3, s0)
        out_3 = self.mux_3.select(4, 5, s0)
        out_4 = self.mux_4.select(6, 7, s0)
        out_5 = self.mux_5.select(8, 9, s0)
        out_6 = self.mux_6.select(10, 11, s0)
        out_7 = self.mux_7.select(12, 13, s0)
        out_8 = self.mux_8.select(14, 15, s0)

        out_9 = self.mux_9.select(out_1, out_2, s1)
        out_10 = self.mux_10.select(out_3, out_4, s1)
        out_11 = self.mux_11.select(out_5, out_6, s1)
        out_12 = self.mux_12.select(out_7, out_8, s1)

        out_13 = self.mux_13.select(out_9, out_10, s2)
        out_14 = self.mux_14.select(out_11, out_12, s2)

        return self.mux_15.select(out_13, out_14, s3)

        
        

    def select_1(self, s, value = None):
        s = bin(s)[:1:-1]
        s = [(2 ** len(s) - 1) * int(i) for i in s]
        z = list(range(0, len(REGISTERS)))

        index = 0

        while(len(z) > 1):
            prev = z.copy()
            z = [self.__mux_2_1__(prev[i], prev[i+1], s[index]) for i in range(0, len(prev), 2)]
            index += 1
    

        address = z[0]
        #If a value was passed, access the register at the given address,
        #else, return the register's value
        if(value):
            if(address != 0):
                REGISTERS[address] = value
        else:
            return REGISTERS[address]

class Adder():
    """Adds two binary numbers
    """

    @staticmethod
    def __half_adder__(a, b) -> tuple:
        """Takes two input values a, b of type string and returns a tuple
        containing the XOR of the inputs and its carry"""
        return (a ^ b, a & b)   #(sum, carry)        

    def add(self, a, b, c = 0) -> tuple:
        """Takes three input values a, b, c and returns the true binary
        addition"""
        s1, c0 = self.__half_adder__(a, b)
        sum_, c1 = self.__half_adder__(c, s1)
        return (sum_, c0 | c1)


class ALU_1Bit():

    def __init__(self):
        self.adder = Adder()
        self.inverter_1 = Inverter()
        self.inverter_2 = Inverter()
        self.result_mux = Two_one_MUX()

    def execute_instruction(self,s0, s1, s2, a, b, carry) -> tuple:
        """Executes a given instruction
        a --> input
        b --> input
        c --> carry (default 0)
        s0 --> logical
        s1 --> invert b
        s2 --> invert a"""

        a = self.inverter_1.invert(a, s2)
        b = self.inverter_2.invert(b, s1)
        sum_, new_carry = self.adder.add(a, b, carry)
        and_gate = a & b

        
        result = self.result_mux.select(sum_, and_gate, s0)
        n = result
        c = negate(s0) & new_carry 
        v = (negate(carry) & negate(s0) & new_carry) | (carry & negate(c) & negate(new_carry))

        return (result, new_carry, n, c, v)
        

class ALU():
    """4-Bit ALu"""

    def __init__(self): 
        self.alu_1bit_1 = ALU_1Bit()
        self.alu_1bit_2 = ALU_1Bit()
        self.alu_1bit_3 = ALU_1Bit()
        self.alu_1bit_4 = ALU_1Bit()

    def execute_instruction(self, instruction, a, b) -> tuple:
        s0, s1, s2 = self.control(instruction)
        a = [int(i) for i in bin(a)[2:].zfill(4)]
        b = [int(i) for i in bin(b)[2:].zfill(4)]

        out_1 = self.alu_1bit_1.execute_instruction(s0, s1, s2, a[3], b[3], s2)
        out_2 = self.alu_1bit_2.execute_instruction(s0, s1, s2, a[2], b[2], out_1[1])
        out_3 = self.alu_1bit_2.execute_instruction(s0, s1, s2, a[1], b[1], out_2[1])
        out_4 = self.alu_1bit_2.execute_instruction(s0, s1, s2, a[0], b[0], out_3[1])

        r = [str(out_4[0]), str(out_3[0]), str(out_2[0]), str(out_1[0])]
        result = int(''.join(r), 2)

        z = negate(out_1[0] | out_2[0] | out_3[0] | out_4[0])
        n = out_4[0]
        c = out_4[3]
        v = out_4[4]

        return (result, z, n, c, v)
        
    def control(self, s) -> tuple:
        s = [int(i) for i in bin(s)[2:]]
        s0 = s[0] & s[1] & negate(s[3])
        s1 = s[0] & s[1] & negate(s[2])
        s2 = s[0] & s[1] & s[2] & negate(s[3])
        return (s0, s1, s2)

        
def two_complement(self, n):
        """Returns the two's complement of a number n"""
        return self.adder.add(inverter(n), 1)
