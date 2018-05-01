import matplotlib.pyplot as plt
import numpy as np
import math
import bitstream


class Modulator:
    def __init__(self, qam=16):
        ''' :param: qam can be 4, 16, 64 '''
        self.data_bits_len = 8
        self.rotation = 0.0
        qam4_mod = [-1.0-1.0j, 1.0-1.0j,
                    -1.0+1.0j, 1.0+1.0j]
        qam4_dem = [[0, 1],
                    [2, 3]]
        qam16_mod = [-3-3j, -1-3j, 1-3j, 3-3j,
                     -3-1j, -1-1j, 1-1j, 3-1j,
                     -3+1j, -1+1j, 1+1j, 3+1j,
                     -3+3j, -1+3j, 1+3j, 3+3j]
        qam16_dem = [[0, 1, 2, 3],
                     [4, 5, 6, 7],
                     [8, 9, 10, 11],
                     [12, 13, 14, 15]]
        if qam == 4:
            self.qam_dem = qam4_dem
            self.qam_mod = qam4_mod
        elif qam == 16:
            self.qam_dem = qam16_dem
            self.qam_mod = qam16_mod
        else:
            dim = int(math.sqrt(qam))
            self.qam_dem = [[x+y*dim
                             for x in range(dim)]
                            for y in range(dim)]
            self.qam_mod = [-dim+2*int(x%dim)+1 + 1j*(2*int(x/dim)-dim+1)
                             for x in range(dim*dim)]
        print(self.qam_mod)
        print(np.mat(self.qam_dem))
        self.qam_dem = np.array(self.qam_dem)
        self.qam_mod = np.array(self.qam_mod)
        self.qam_mod /= math.sqrt(np.max(np.imag(self.qam_mod**2)))  # norm to one

    def iq_mod(self, symbol):
        """
        00 | 01
        ---|---
        10 | 11
        :rtype: complex value
        """
        assert 0 <= symbol < len(self.qam_mod)
        assert type(symbol) is int
        return self.qam_mod[symbol] * np.exp(1.0j*self.rotation)

    def iq_dem(self, c):
        """ from a given complex value
        codem in qam4 return symbol
        :rtype: int
        """
        d0, d1 = self.qam_dem.shape
        D = max(d0, d1)  # srednica konstelacji
        R = 2**0.5/2
        c = c * np.exp(-1.0j*self.rotation)  # back rotation
        assert -1.0 <= np.real(c) <= 1.0
        assert -1.0 <= np.imag(c) <= 1.0
        i, q = np.real(c), np.imag(c)  # -1..1 circle
        i, q = [(v+R)/R for v in (i, q)]  # 0..2 from square
        i, q = [int(round(v*(D-1)/2)) for v in (i, q)]  # {0..D}
        assert 0 <= i < D
        assert 0 <= q < D
        return self.qam_dem[q, i]

    def modulate(self, data):
        """ generate list of complex value (i, q) pairs from a given data """
        symbol_len = self.qam_dem.shape[0]
        stream = bitstream.Bitstream()
        stream.writeall(data, self.data_bits_len)
        symbols = stream.readall(symbol_len)
        complex = [Modulator.iq_mod(self, s) for s in symbols]
        return complex

    def demodulate(self, complex_series):
        """ generate list of data from a given complex series of iq data """
        symbol_len = self.qam_dem.shape[0]
        stream = bitstream.Bitstream()
        for c in complex_series:
            symbol = self.iq_dem(c)
            stream.write(symbol, symbol_len)
        return stream.readall(self.data_bits_len)


if __name__ == "__main__" or True:
    print("|===============================|")
    print("|        Bitstream demo         |")
    print("| Author: Karol Trzciński, 2018 |")
    print("|===============================|")
    print("")

    mod = Modulator()
    data = [0, 1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

    mod_data = mod.modulate(data)
    dem_data = mod.demodulate(mod_data)

    mod.rotation = np.pi / 8
    mod_rot_data = mod.modulate(data)
    dem_rot_data = mod.demodulate(mod_rot_data)

    print("input data: " + str(data))
    print("mod_data: " + str(mod_data))
    print("dem_data: " + str(dem_data))
    print("")
    print("rotate constelation: " + str(mod.rotation))
    print("mod_rot_data: " + str(mod_rot_data))
    print("dem_rot_data: " + str(dem_rot_data))
    print("")
    plot_constelation = True  # input("Plot constelation? ")

    if plot_constelation:
        deg = int(mod.rotation*180/np.pi)
        t = np.linspace(0, 2*np.pi, 200)
        plt.plot(np.sin(t), np.cos(t), 'g', label="unit circle")
        plt.plot(np.real(mod_data), np.imag(mod_data), 'bo', label="rot=0")
        plt.plot(np.real(mod_rot_data), np.imag(mod_rot_data),  'rx', label="rot="+str(deg)+"deg")
        plt.legend()
        plt.grid()
        plt.axis('equal')
        plt.title('IQ constelation')
        plt.show()
