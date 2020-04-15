import math
import operator
import LTDrop
from LTUtil import *


class LTDecodedFile:
    filename = ""
    file_size = 0
    chunk_amount = 0
    drops = {}
    chunks_drop_dict = {}
    loaded_Drops = 0

    def has_chunk(self, index):
        return self.chunks_drop_dict[index] in self.drops
        #return math.pow(2, index) in self.drops

    def reconstructed_chunks(self):
        reconstructed = 0
        for i in range(0, self.chunk_amount):
            if self.has_chunk(i):
                reconstructed += 1
        return reconstructed

    def is_complete(self):
        for i in range(0, self.chunk_amount):
            if not self.has_chunk(i):
                return False
        return self.chunk_amount > 0

    def add_drop(self, drop):
        if self.filename == "":
            self.filename = drop.filename
        if self.file_size == 0:
            self.file_size = drop.file_size
        if self.chunk_amount == 0:
            self.chunk_amount = drop.chunk_amount
            for i in range(0, self.chunk_amount):
                self.chunks_drop_dict[i] = int(math.pow(2, i))
        drop_name = drop.bitvector
        if drop.file_size != self.file_size or drop.filename != self.filename or drop.chunk_amount != self.chunk_amount:
            print(f'Discarded drop {drop_name}')
        else:
            self.drops[drop_name] = drop
            self.loaded_Drops += 1
            print(f'Added drop {drop_name}')

    def process(self):  # Returns True if drops were generated
        self.cleanup_drops()
        new_drops = {}
        delete_drops_list = []
        for primary in (sorted(self.drops.values(), key=operator.attrgetter('bitcount'), reverse=True)):
            for secondary in (sorted(self.drops.values(), key=operator.attrgetter('bitcount'), reverse=True)):
                if secondary.bitcount > primary.bitcount and secondary.bitvector not in delete_drops_list:
                    new_drop = self.try_generating_drop(primary.bitvector, secondary.bitvector, new_drops)
                    if new_drop != None:
                        new_drops[new_drop.bitvector] = new_drop
                        delete_drops_list.append(secondary.bitvector)

        self.drops.update(new_drops)
        self.delete_drops(delete_drops_list)
        return bool(new_drops)

    def old_process(self):  # Returns True if drops were generated
        self.cleanup_drops()
        new_drops = {}
        delete_drops_list = []
        for primary_index in self.drops:
            for secondary_index in self.drops:
                if secondary_index > primary_index and secondary_index not in delete_drops_list:
                    new_drop = self.try_generating_drop(primary_index, secondary_index, new_drops)
                    if new_drop != None:
                        exit = True
                        new_drops[new_drop.bitvector] = new_drop
                        if not is_pow_of_two(secondary_index):
                            isPowTwo = is_pow_of_two(primary_index)
                            if not isPowTwo and count_bits(primary_index) > count_bits(secondary_index):
                                delete_drops_list.append(primary_index)
                                break
                            else:
                                delete_drops_list.append(secondary_index)
                        elif not is_pow_of_two(primary_index):
                            delete_drops_list.append(primary_index)
                            break

        self.drops.update(new_drops)
        self.delete_drops(delete_drops_list)
        return bool(new_drops)

    def try_generating_drop(self, primary_index, secondary_index, new_drops):
        result_bV = primary_index ^ secondary_index
        if result_bV not in self.drops and result_bV not in new_drops:
            result_bitcount = count_bits(result_bV)
            primary_bitcount = count_bits(primary_index)
            secondary_bitount = count_bits(secondary_index)
            if result_bitcount < primary_bitcount or result_bitcount < secondary_bitount:
                if len(self.drops[primary_index].payload) == len(self.drops[primary_index].payload):
                    result_payload = byte_xor(self.drops[primary_index].payload, self.drops[secondary_index].payload)
                    new_drop = LTDrop.LTDrop(self.filename, self.file_size, self.drops[primary_index].chunk_size, self.chunk_amount, result_bV, result_payload)
                    return new_drop
                else:
                    raise Exception("Payload size mismatch")

    def cleanup_drops(self):
        delete_drops_list = []
        for index in self.drops:
            if not is_pow_of_two(index):
                keep = False
                for pOfTwo in self.chunks_drop_dict.values():
                    if index & pOfTwo == pOfTwo and pOfTwo not in self.drops:
                        keep |= True
                        break
                if not keep:
                    delete_drops_list.append(index)
        self.delete_drops(delete_drops_list)

    def delete_drops(self, delete_drops_list):
        for i in range(0, len(delete_drops_list)):
            if delete_drops_list[i] in self.drops:
                del self.drops[delete_drops_list[i]]


    def save(self, output_folder):
        if not self.is_complete():
            raise Exception("File incomplete, can't save")
        with open(output_folder + "/" + self.filename, 'wb') as output_file:
            for index in range(0, self.chunk_amount-1):
                output_file.write(self.drops[math.pow(2, index)].payload)

            last_chunk_drop = self.drops[math.pow(2, self.chunk_amount-1)]
            last_part_size = self.file_size % last_chunk_drop.chunk_size
            last_bytes = last_chunk_drop.payload[:last_part_size]
            output_file.write(last_bytes)

    #@staticmethod
    #def bitvector_xor(bV1, bV2):
     #   int_res = bV1.vector[0] ^ bV2.vector[0]
     #   res = BitVector(size=bV1.size)
     #   res.vector[0] = int_res
     #   return res

    def chunks_per_drop_data(self):
        output = []
        for bitvector in self.drops:
            output.append(count_bits(bitvector))
        return output

