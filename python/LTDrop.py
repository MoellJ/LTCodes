import math
from LTUtil import *
from BitVector import BitVector

class LTDrop:

    def __init__(self, filename, size, chunk_size, chunk_amount, bitvector, dropData):
        if len(dropData) != chunk_size:
            raise Exception("Wrong payload size")
        #if len(bitvector) != math.ceil(size / chunk_size):
        #    raise Exception("Bitvector incompatible")
        self.filename = filename
        self.file_size = size
        self.chunk_size = chunk_size
        self.chunk_amount = chunk_amount
        self.bitvector = bitvector
        self.payload = dropData
        self.bitcount = count_bits(bitvector)

    def save(self, folder_path):
        #bitvectorInt = self.bitvector.vector[0]
        with open(folder_path + "/" + str(self.bitvector) + ".drop", 'wb') as output_file:
            nameBytes = bytes(self.filename, 'utf-8')
            nameBytesLength = (len(nameBytes)).to_bytes(2, byteorder='big')
            output_file.write(nameBytesLength)                                  # 2 Bytes for name length
            output_file.write(nameBytes)                                        # X Bytes for name
            output_file.write((self.file_size).to_bytes(8, byteorder='big'))    # 8 Bytes for file size
            output_file.write((self.chunk_size).to_bytes(4, byteorder='big'))   # 4 Bytes for chunk size
            #bitvectorLength = len(self.bitvector)

            output_file.write(self.chunk_amount.to_bytes(8, byteorder='big'))   # 8 Bytes for bitvector length
            bitvectorLengthInBytes = math.ceil(self.chunk_amount/8)
            bitvectorBytes = self.bitvector.to_bytes(bitvectorLengthInBytes, byteorder='big')
            output_file.write(bitvectorBytes)                                   # X Bytes for bitvector
            output_file.write(self.payload)                                     # chunk_size Bytes for payload



def load(drop_path):
    in_bytes = get_bytes_from_file(drop_path)
    nameBytesLength = int.from_bytes(in_bytes[:2], byteorder='big')
    in_bytes= in_bytes[2:]                                                      # 2 Bytes for name length
    filename = in_bytes[:nameBytesLength].decode('utf-8')
    in_bytes = in_bytes[nameBytesLength:]                                       # X Bytes for name
    input_file_size = int.from_bytes(in_bytes[:8], byteorder='big')
    in_bytes = in_bytes[8:]                                                     # 8 Bytes for file size
    chunk_size = int.from_bytes(in_bytes[:4], byteorder='big')
    in_bytes = in_bytes[4:]                                                     # 4 Bytes for chunk size
    chunk_amount = int.from_bytes(in_bytes[:8], byteorder='big')
    in_bytes = in_bytes[8:]                                                     # 8 Bytes for bitvector length
    bitvectorLengthInBytes = math.ceil(chunk_amount / 8)
    bitvector = int.from_bytes(in_bytes[:bitvectorLengthInBytes], byteorder='big')
    in_bytes = in_bytes[bitvectorLengthInBytes:]                                # X Bytes for bitvector
    if len(in_bytes) != chunk_size:                                             # chunk_size Bytes for payload
        raise Exception('Something went wrong while parsing')
    return LTDrop(filename, input_file_size, chunk_size, chunk_amount, bitvector, in_bytes)



