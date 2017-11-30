# -*- coding: utf8 -*-
import math

class BloomFilter:
    def __init__(self, list_size):
        """ Create a bit array of a specific size """
        self.size = list_size*20
        self.bitarray = bytearray(self.size/8+1)
        self.k = 10

    def BKDRHash(self, key, seed_number):
            seed_list = [13, 31, 313, 131, 1313, 3131, 13131, 131313, 1313131, 313131]
            seed = seed_list[seed_number]
            hash = 0
            for i in range(len(key)):
              hash = (hash * seed) + ord(key[i])
            return hash

    def set(self, n):
        """ Sets the nth element of the bitarray """

        index = n / 8
        position = n % 8
        self.bitarray[index] = self.bitarray[index] | 1 << (7 - position)

    def get(self, n):
        """ Gets the nth element of the bitarray """
        
        index = n / 8
        position = n % 8
        return (self.bitarray[index] & (1 << (7 - position))) > 0 

    def add(self, key):
        for i in range(self.k):
            self.set(self.BKDRHash(key, i) % self.size)

    def query(self, key):
        for i in range(self.k):
            if not self.get(self.BKDRHash(key, i) % self.size):
                return False
        return True

            
if __name__ == "__main__":
    pass