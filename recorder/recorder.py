import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import collections
import logging

import wave

from utils.parser import parse_arguments
from utils.logger import create_logger


def main(args):
    # change matplot lib backend
    matplotlib.use('TKAgg')


    # Audio chunk, samples per frame
    CHUNK = args.CHUNK_SIZE
    # sample format
    FORMAT = pyaudio.paInt16
    #Mono
    CHANNELS = 1
    # samples per secound
    RATE = args.SAMPLE_RATE

    # 
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK
    )

    #Ring buffer
    data = collections.deque(maxlen=5*CHUNK)
    #fill with zeros
    for zero in range(5*CHUNK):
        data.append(0)

    fig, ax = plt.subplots()

    #length of x axis
    x = np.arange(0, 5*CHUNK, 1)
    line, = ax.plot(x, np.random.randint(-2**16, 2**16, CHUNK*5))




    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * 5)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open('test.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # plt.show(block=False)
    # while True:
    #     # raw (bytes)
    #     new_data = stream.read(CHUNK)
    #     # as int
    #     new_data  = struct.unpack(str(CHUNK) + 'h', new_data)

    #     # add sample to buffer
    #     for sample in new_data:
    #         data.append(sample)

    #     line.set_ydata(np.array(data))

    #     fig.canvas.draw()
    #     fig.canvas.flush_events()

if __name__ == "__main__":
    logger =  create_logger("recorder")
    args = parse_arguments()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("set verbose logging mode")
    
    main(args)

    exit(0)
