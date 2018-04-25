import matplotlib.pyplot as plt
import numpy as np
import math
import bitstream


class Modulator:
    def __init__(self):
        self.data_bits_len = 8
        self.rotation = 0.0
        qam4_mod = np.array([-1.0+1.0j, 1.0+1.0j, -1.0-1.0j, 1.0-1.0j])
        self.qam_mod = qam4_mod
        self.qam_mod /= math.sqrt(np.max(np.imag(self.qam_mod**2)))  # norm to one
        self.qam_dem = np.array([[2, 3],
                           [0, 1]])

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
        D = self.qam_dem.shape[0]  # srednica konstelacji
        c = c * np.exp(-1.0j*self.rotation)  # back rotation
        c = np.round(c * math.sqrt(D))  # -1..1
        assert -1.0 <= np.real(c) <= 1.0
        assert -1.0 <= np.imag(c) <= 1.0
        i, q = np.real(c), np.imag(c)
        i, q, = int((i+0.5*D)/D), int((q+0.5*D)/D)  # {0..D}
        assert 0 <= i < 2
        assert 0 <= q < 2
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


if __name__ == "__main__":
    print("|===============================|")
    print("|        Bitstream demo         |")
    print("| Author: Karol Trzciński, 2018 |")
    print("|===============================|")
    print("")

    mod = Modulator()
    data = [1, 2, 3, 5, 129]

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
