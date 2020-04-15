import math
import threading
import LTDrop
import LTDecodedFile
import tkinter as tk
from tkinter import filedialog
from tkinter import *


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np



class DecodeSession:

    canvas_width = 500
    canvas_height = 500
    processing_thread = None
    processing = False


    def __init__(self):
        self.master = Tk()
        self.master.title("Painting using Ovals")
        top_frame = Frame(self.master)
        self.load_button = Button(top_frame, text="Load more", command=self.open_files)
        self.load_button.pack(side=LEFT)
        self.save_button = Button(top_frame, text="Save file", command=self.save_file)
        self.save_button['state'] = 'disabled'
        self.save_button.pack(side=LEFT)

        self.gui_text = StringVar()
        self.gui_text.set(f'Loaded Drops: 0 '
                         f'\nCurrent Drops: 0 '
                         f'\nExpected Chunks: 0 '
                         f'\nReconstructed Chunks: 0(0%)')
        text_out = tk.Label(top_frame, textvariable=self.gui_text)
        text_out.pack(side=RIGHT)

        top_frame.pack(side=TOP, fill="both", expand=False)

        canvas_frame = Frame(self.master)

        self.chunk_canvas = Canvas(canvas_frame,
                                   width=self.canvas_width,
                                   height=self.canvas_height)
        self.chunk_canvas.pack(side=LEFT,expand=YES, fill=BOTH)
        self.currentFile = LTDecodedFile.LTDecodedFile()

        self.histo_figure = Figure(figsize=(5, 5), dpi=100)
        self.histo_figure._remove_ax
        self.histogram = self.histo_figure.gca()

        self.histo_canvas = FigureCanvasTkAgg(self.histo_figure, canvas_frame)
        self.histo_canvas.draw()
        self.histo_canvas.get_tk_widget().pack(side=RIGHT, fill=tk.BOTH, expand=True)
        self.histo_canvas._tkcanvas.pack(side=RIGHT, fill=tk.BOTH, expand=True)

        canvas_frame.pack(fill="both", expand=False)

        self.open_files()
        self.draw()
        self.mainloop()

    def mainloop(self):
        while True:
            try:
                self.draw()
            except:
                pass
            if self.processing_thread is not None:
                if not self.processing_thread.is_alive() and self.processing:
                    self.processing_thread = None
                    self.processing = False
                    self.load_button['state'] = 'normal'
                    if self.currentFile.is_complete():
                        self.save_button['state'] = 'normal'
                        self.load_button['state'] = 'disabled'
            #try:
            self.master.update()
            self.master.update_idletasks()
            #except:
            #    pass

    def draw(self):
        self.update_text()
        if len(self.currentFile.drops) > 0:
            self.draw_histogram()
            self.chunk_canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill="#FFFFFF")
            chunk_amount = self.currentFile.chunk_amount
            if chunk_amount > 0:
                rowcols = math.ceil(math.sqrt(chunk_amount))
                chunk_width = self.canvas_width / rowcols
                chunk_height = self.canvas_height / rowcols
                for i in range(0, rowcols):
                    for j in range(0, rowcols):
                        chunk_index = i * rowcols + j
                        if chunk_index < chunk_amount:
                            f = "#AAAAAA"
                            if self.currentFile.has_chunk(chunk_index):
                                f = "#00FF00"
                            self.chunk_canvas.create_rectangle(j * chunk_width, i * chunk_height, (j + 1) * chunk_width, (i + 1) * chunk_height, outline="#000000", fill=f)
                            self.chunk_canvas.create_text((j +0.5) * chunk_width, (i + 0.5) * chunk_height, text="2^"+str(int(chunk_index)))


    def draw_histogram(self):
        data = self.currentFile.chunks_per_drop_data()
        bins = max(data)
        self.histogram.clear()
        self.histogram.set_xticks(list(range(1,bins+1)))
        self.histogram.hist(data, bins=np.arange(bins+1)+0.5, color="blue", ec='black')
        self.histogram.set_xlabel('Chunk / Drop', fontsize=15)
        self.histogram.set_ylabel('Frequency', fontsize=15)
        self.histo_canvas.draw()

    def update_text(self):
        loadedDrops = self.currentFile.loaded_Drops
        currentDrops = len(self.currentFile.drops)
        expectedChunks = self.currentFile.chunk_amount
        reconstructed = self.currentFile.reconstructed_chunks()
        reconstructedPerc = 0
        if expectedChunks != 0:
            reconstructedPerc = int(reconstructed * 100 / expectedChunks)
        self.gui_text.set(f'Loaded Drops: {loadedDrops} '
                         f'\nCurrent Drops: {currentDrops} '
                         f'\nExpected Chunks: {expectedChunks} '
                         f'\nReconstructed Chunks: {reconstructed}({reconstructedPerc}%)')


    def open_files(self):
        if self.processing_thread is None:
            drop_file_path = filedialog.askopenfilenames()
            self.load_button['state'] = 'disabled'
            self.processing = True
            self.processing_thread = threading.Thread(target=self.load_and_process_thread, args=[drop_file_path])
            self.processing_thread.start()
            self.draw()

    def load_and_process_thread(self, drop_file_path):
        for i in range(0, len(drop_file_path)):
            drop = LTDrop.load(drop_file_path[i])
            self.currentFile.add_drop(drop)
        while self.currentFile.process():
            continue

    def save_file(self):
        output_folder_path = filedialog.askdirectory()
        self.currentFile.save(output_folder_path)

def main():
    DecodeSession()

if __name__ == "__main__":
        main()

