import os
import sys
import math
import random
import LTDrop
import tkinter as tk
from tkinter import filedialog
from BitVector import BitVector
from LTUtil import *

#chunk_size = 1048576
#chunk_size = 1024


def main():
    root = tk.Tk()
    root.withdraw()

    input_file_path = filedialog.askopenfilename()
    print(input_file_path)
    output_folder_path = filedialog.askdirectory()

    input_file_size = os.path.getsize(input_file_path)
    print(f'File Size: {input_file_size} Bytes')
    #Ask for chunk size
    chunk_size = inputNumber("How big should one drop be (in Kilobytes) ") * 1024
    chunk_amount = math.ceil(input_file_size/chunk_size)
    print(f'Will split into {chunk_amount} chunks')
    input_file_bytes = get_bytes_from_file(input_file_path)
    input_file_chunks = []
    for i in range(0, len(input_file_bytes), chunk_size):
        input_file_chunks.append(input_file_bytes[i:i + chunk_size])
    #Fill up last chunk:
    input_file_chunks[-1] = input_file_chunks[-1] + b'\0'*(chunk_size - len(input_file_chunks[-1]))
    #Ask for amount of drops
    amount_of_drops = inputNumber("How many drops should be produced? ")
    for dropNo in range(0, amount_of_drops):
        bitlist = generate_bitvector(chunk_amount)
        #bitlist = [0,0,1,0,1,1,0,1,0]
        dropData = generate_drop_data(input_file_chunks, bitlist)
        bitvector = BitVector(bitlist=bitlist[::-1])
        drop = LTDrop.LTDrop(os.path.basename(input_file_path), input_file_size, chunk_size, chunk_amount, bitvector.intValue(), dropData)
        drop.save(output_folder_path)

def generate_bitvector(chunk_amount):
    bitvector = [0] * chunk_amount
    d = soliton_distribution(chunk_amount)
    for i in range(0, d):
        while True:
            index = random.randint(0, chunk_amount-1)
            if bitvector[index] != 1:
                bitvector[index] = 1
                break
    return bitvector


def generate_drop_data(input_file_chunks, bitvector):
    output = b'\0' * len(input_file_chunks[0])
    for i in range(0, len(input_file_chunks)):
        if bitvector[i] == 1:
            output = byte_xor(output, input_file_chunks[i])
    return output

def soliton_distribution(N):
    while 1:
        x = random.random()  # Uniform values in [0, 1)
        i = int(math.ceil(1 / x))  # Modified soliton distribution
        return i if i <= N else 1  # Correct extreme values to 1

def inputNumber(message):
    while True:
        try:
            userInput = int(input(message))
        except ValueError:
            print("Not an integer! Try again.")
            continue
        else:
            return userInput
            break



if __name__ == "__main__":
    main()

