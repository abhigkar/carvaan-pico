#https://github.com/SnijderC/dyplayer/blob/main/src/DYPlayer.cpp

import board
import time
import busio
import struct


class DYPlayer(object):

    # --- constants   ----------------------------------------------------------

    EQ_NORMAL = 0
    EQ_POP = 1
    EQ_ROCK = 2
    EQ_JAZZ = 3
    EQ_CLASSIC = 4

    STATUS_STOPPED = 0
    STATUS_BUSY = 1
    STATUS_PAUSED = 2

    # --- constructor   --------------------------------------------------------

    def __init__(self, uart=None, media=None, volume=20, eq=None, latency=0.100):
        if uart is None:
            self._uart = busio.UART(board.TX, board.RX, baudrate=9600)
        else:
            self._uart = uart
        self._latency = latency

        self.setVolume(volume)
        #self.set_eq(eq if eq else DYPlayer.EQ_NORMAL)

    # --- transfer data to device   ---------------------------------------------

    def _calculate_checksum(self, data):
        sum = 0
        for i in range(len(data)):
            sum += data[i]
        return sum & 0xff

    def _validate_crc(self, data, len):
        crc = data[-1]
        return self._calculate_checksum(data[:-1]) == crc

    def _get_response(self, length):
        if self._uart.in_waiting:
            buf = self._uart.read(length)
            if (
                buf is not None
                and len(buf) == length
                and self._validate_crc(buf, length)
            ):
                return buf
            return None

    def _write_data(self, cmd):
        self._uart.write(bytes(cmd))  # Command word
        time.sleep(self._latency)  # other commands
        
    def play(self):
        self._write_data([0xaa, 0x02, 0x00, 0xac])
           
    def pause(self):
        self._write_data([0xaa, 0x03, 0x00, 0xad])
        
    def stop(self):
        self._write_data([0xaa, 0x04, 0x00, 0xae])
       
    def previous(self):
        self._write_data([0xaa, 0x05, 0x00, 0xaf])

    def next(self):
        self._write_data([0xaa, 0x06, 0x00, 0xb0])
        
    def playSpecified(self, number):
        command = [0xaa, 0x07, 0x02, 0x00, 0x00, 0x00]
        command[3] = (number >> 8) & 0xff
        command[4] = number & 0xff
        command[5] = self._calculate_checksum(command)
        self._write_data(command)

    def checkPlayState(self):
        command = [0xaa, 0x01, 0x00, 0xab]
        self._write_data(command)
        time.sleep(.500)
        res = self._get_response(5)
        if res is not None:
           return res[3]
        else:
           return None
    
    def setVolume(self, volume):
        if volume > 30:
            volume = 30
        command = [0xaa, 0x13, 0x01, volume,0x00]
        command[4] = self._calculate_checksum(command)
        self._write_data(command)
        
    def volumeIncrease(self):
        self._write_data([0xaa, 0x14, 0x00,0xbe])
        
    def volumeDecrease(self):
        self._write_data([0xaa, 0x15, 0x00,0xbf])
        
    def setVolume(self, volume):
        command = [0xaa, 0x13, 0x01, 0x00, 0x00]
        command[3] = volume
        command[4] = self._calculate_checksum(command)
        self._write_data(command)
        
    
    #Normal:0, Pop:1, Rock:2, Jazz:3, Classic:4
    def setEq(self, eqlzr):
        command = [0xaa, 0x1a, 0x01, 0x00, 0x00]
        command[3] = eqlzr
        command[4] = self._calculate_checksum(command,4)
        self._write_data(command)
        
        
        

