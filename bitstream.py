import math

class Bitstream:
    def __init__(self):
        self.buf = []

    def write(self, x, in_data_bits_len):
        ''' read \in_data_bits_len bits from stream '''
        assert in_data_bits_len >= 0
        temp = [x >> i for i in range(in_data_bits_len)]
        temp = [t % 2 for t in temp]
        self.buf.extend(temp)

    def writeall(self, in_table, in_data_bits_len):
        ''' write all data from \in_table to a stream'''
        for d in in_table:
            self.write(d, in_data_bits_len)

    def read(self, out_data_bits_len):
        ''' read \out_data_bits_len bits from stream '''
        assert out_data_bits_len >= 0
        if len(self.buf) == 0:
            return None
        if len(self.buf) < out_data_bits_len:
            out_data_bits_len = len(self.buf)
        temp = [v << i for i, v in enumerate(self.buf[0:out_data_bits_len])]
        del self.buf[0:out_data_bits_len]
        ret = sum(temp)
        return ret

    def readall(self, out_data_bits_len):
        ''' read all data from stream in \out_data_bits_len chunks '''
        out_len = math.floor(len(self.buf)/out_data_bits_len)
        return [self.read(out_data_bits_len) for _ in range(out_len)]

if __name__ == "__main__":
    print("|===============================|")
    print("|        Bitstream demo         |")
    print("| Author: Karol Trzciński, 2018 |")
    print("|===============================|")
    print("")
    in_data = [0, 1, 2, 4, 24]
    in_data_bits_len = 8
    out_data_bits_len = 4

    # create buffer and write all data
    stream = Bitstream()
    stream.write(in_data[0], in_data_bits_len)
    stream.writeall(in_data[1:], in_data_bits_len)

    # read all data from stream
    out_first = stream.read(out_data_bits_len)
    out_data = stream.readall(out_data_bits_len)

    # concantenate readed data
    out_data = [out_first] + out_data

    # print experiment results
    print("for a input bits len equal " + str(in_data_bits_len))
    print("output bits len equal " + str(out_data_bits_len))
    print("and input data equal " + str(in_data))
    print("output is " + str(out_data))
