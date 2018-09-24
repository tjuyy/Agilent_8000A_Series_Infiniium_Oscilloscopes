# -*- coding: utf-8 -*-
import visa
import os
import sys
import time
from struct import unpack
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'NSimSun,Times New Roman'


def unsigned_byte_to_signed_byte(byte):
    if byte > 127:
        return (256 - byte) * (-1)
    else:
        return byte

def init(inst, memory_depth, sample_rate='AUTO'):
    if memory_depth > 4100000:
        memory_depth = 4100000
    # init
    inst.write("*RST")
    inst.write(":CLS")
    inst.write(":SYSTem:HEADer OFF")
    # timebase setup
    inst.write(":TIMebase:SCALE 5e-6")
    inst.write(":TIMebase:REF CENT")
    # Vertical setup
    inst.write(":CHANnel1:RANGe 8;OFFSet 0e-3")
    # trigger setup
    inst.write(":TRIGger:SOURce Channel1")
    inst.write(":TRIGger:LEVel CHANnel1,0")
    inst.write(":TRIGger:MODE EDGE")
    inst.write(":TRIG:Slope POS")
    # acquire mode setup
    inst.write(
        ":ACQuire:MODE RTIMe;AVERage OFF;POINts {}".format(memory_depth))
    inst.write(':ACQuire:SRATe {}'.format(sample_rate))

def acquire_ascii(inst, read_length):
    Channel = 'CHANnel1'
    f = open("data_output.csv", 'w')

    # acquire mode setup
    inst.write(":ACQuire:MODE RTIMe;AVERage OFF;POINts {}".format(read_length))

    # Digitize the Waveform that is showing on display
    inst.write(":DIGitize CHANnel1")
    inst.write(":CHANnel1:DISPlay ON")

    #Setup waveform transfer
    # inst.write(":WAV:BYTeorder LSBFIRST")
    inst.write(":WAV:SOURCE CHANnel1")
    # print(inst.query(":WAVeform:FORMat?"))
    inst.write(":WAVeform:FORMat ASCii")
    # print(inst.query(":WAVeform:FORMat?"))

    finalpath = "_".join(
        ["Ascii_data",
         time.strftime("%Y%m%d_%H%M%S.csv", time.localtime())])
    f = open(finalpath, 'w')
    inst.write(':SYSTEM:HEADER OFF')

    buffersize = 1000
    outstr = ''
    times = read_length // buffersize
    r = read_length % buffersize
    if times > 0:
        for i in range(times):
            inst.write(':WAV:DATA? {},{}'.format((1 + i * buffersize),
                                                 buffersize))
            data = inst.read_raw()
            outstr += data.decode('utf8', "ignore").replace(',', '\n')
            print('Capturing ...', end='')
            process_bar = (i + 1) / (times + 1)  # process_bar
            print('#' * int(20 * process_bar),
                  '.' * int(20 - 20 * process_bar), '[{0:2.2f}%]'.format(
                      100 * process_bar))  # print process bar
        if read_length % buffersize:
            inst.write(':WAV:DATA? {},{}'.format((1 + (i + 1) * buffersize),
                                                 r))
            data = inst.read_raw()
            outstr += data.decode('utf8', "ignore").replace(',', '\n')
        print('Capturing ...', end='')
        process_bar = 1
        print('#' * int(20 * process_bar), '.' * int(20 - 20 * process_bar),
              '[{0:2.2f}%]'.format(100 * process_bar))  # print process bar
    else:
        inst.write(':WAV:DATA? 1,{}'.format(read_length))
        data = inst.read_raw()
        outstr += data.decode('utf8', "ignore").replace(',', '\n')
        print('Capturing ...', end='')
        process_bar = 1
        print('#' * int(20 * process_bar), '.' * int(20 - 20 * process_bar),
              '[{0:2.2f}%]'.format(100 * process_bar))  # print process bar
    f.write(outstr)
    f.close()

    print('Finished, Storaged ascii data to: ' + os.path.join(pwd, finalpath))
    return os.path.join(pwd, finalpath)


def plot_figure(path):
    x = np.loadtxt(path)
    plt.plot(x, label='Channel 1')
    plt.xlabel('index')
    plt.ylabel('Voltage')
    plt.title('Channel 1 Voltage')
    plt.legend()
    plt.show()


# return bytes length to read 
def SetupDataTransfer(inst):
    x = inst.read_bytes(count=1, chunk_size=None, break_on_termchar=False)
    # 1st byte'#'
    L = inst.read_bytes(count=1, chunk_size=None, break_on_termchar=False)
    # 2bd byte L indicate length of bytes to read
    bytes_to_read = L[0] - ord('0')
    x = inst.read_bytes(bytes_to_read, chunk_size=None)
    bytes_to_read = x.decode('ascii')
    # print(int(bytes_to_read))
    return int(bytes_to_read)


def transfer_word_voltages(inst, read_length):
    inst.write(":DIGitize CHANnel1")
    inst.write(":CHANnel1:DISPlay ON")

    # Setup waveform transfer
    # inst.write(":WAV:BYTeorder LSBFIRST")
    inst.write(":WAV:SOURCE CHANnel1")
    inst.write(":WAVeform:FORMat WORD")
    inst.write(":WAVeform:BYTeorder LSBFirst")  # little endian

    # Query scaling information for translating to real voltages and times
    # yref = float(inst.query(":WAVeform:YREFerence?"))
    yorg = float(inst.query(":WAVeform:YORigin?"))
    yinc = float(inst.query(":WAVeform:YINCrement?"))
    # xref = float(inst.query(":WAVeform:XREFerence?"))
    xorg = float(inst.query(":WAVeform:XORigin?"))
    xinc = float(inst.query(":WAVeform:XINCrement?"))
    # xref,yref always zero in this oscilloscope

    # print('yref=', yref)
    # print('yorg=', yorg)
    # print('yinc=', yinc)
    # print('xref=', xref)
    # print('xorg=', xorg)
    # print('xinc=', xinc)

    inst.write(':WAV:DATA? 1,{}'.format(read_length))
    bytes_to_read = SetupDataTransfer(inst)
    wordData = inst.read_bytes(bytes_to_read, chunk_size=None)
    termination = inst.read_bytes(1, chunk_size=None)
    # read termination character '\n'

    intData = unpack('<' + 'h' * (len(wordData) // 2), wordData)
    # < little endian
    # > big endian
    # 'h' signed
    # 'H' unsigned
    voltagesList = []
    timeList = []
    for item in intData:
        voltagesList.append(item * yinc + yorg)
    timeList = [time * xinc + xorg for time in range(read_length)]
    # for time in range(read_length):
    #     timeList.append(time * xinc + xorg)
    return [timeList, voltagesList]


def plotXY(x, y):
    plt.plot(x, y, label='Channel 1')
    plt.xlabel('time(s)')
    plt.ylabel('Voltage(V)')
    plt.title('Channel 1 Voltage')
    plt.legend()
    plt.show()


def storage_to_file(x):

    finalpath = "_".join(
        ["data", time.strftime("%Y%m%d_%H%M%S.csv", time.localtime())])
    f = open(finalpath, 'w')
    for i in range(len(x)):
        f.write('{0:.4e}\n'.format(x[i]))
    f.close()


def main():
    print(sys.version)
    rm = visa.ResourceManager()
    # print(rm.list_resources())
    # inst = rm.open_resource('GPIB0::7::INSTR', query_delay=1)  # set query_delay after each command
    inst = rm.open_resource('GPIB0::7::INSTR')  # GPIB address
    inst.chunk_size = 102400
    inst.timeout = 10000
    inst.read_termination = '\n'
    print(inst.query('*IDN?'))

    # initialize, set memory_depth & sample_rate
    init(inst, memory_depth=400000, sample_rate='1G')
    # sample rate available value (Sa/s)
    # 0.5   1   2   2.5  4   5   10  20  25  40  50  100  200  250  400
    # 500   1k  2k  2.5k 4k  5k  10k 20k 25k 40k 50k 100k 200k 250k 400k
    # 500k  1M  2M  2.5M 4M  5M  10M 20M 25M 40M 50M 100M 125M 200M 250M
    # 500M  1G  2G  4G
    
    # set read length
    [time, voltages] = transfer_word_voltages(inst, read_length=20000)
    # storage to csv file
    storage_to_file(voltages)
    # plot XY Garph
    plotXY(time, voltages)

    # p = acquire_ascii(inst, read_length=4000)
    # plot_figure(p)

    inst.close()



pwd = os.getcwd()

if __name__ == '__main__':
    print('Start at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    main()
    print('Finished at ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
