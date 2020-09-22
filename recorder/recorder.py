from utils.logger import create_logger
from utils.parser import parse_arguments
import wave
import logging
import collections
import matplotlib.pyplot as plt
import pyaudio
import struct
import time
import numpy as np
import matplotlib
# matplotlib.use('Gtk3Agg')
matplotlib.use('TKAgg')


# Buffer size in sec
RECORD_BUFFER_SIZE = 5
# Threshold when amplitude is high (% of max amplitude)
RECORD_THRESHOLD = 0.015

def main(args):
    # Audio chunk, samples per frame
    CHUNK = args.CHUNK_SIZE
    # sample format
    FORMAT = pyaudio.paInt16
    y_range = 2**16
    # Mono
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

    # Record Buffer - Ring buffer
    data = collections.deque(maxlen=RATE * RECORD_BUFFER_SIZE)
    # fill with zeros
    for _ in range(data.maxlen):
        data.append(0)

    # preprocess absolute amplitude threshold
    recording_amplitude_limit = (y_range / 2) * RECORD_THRESHOLD

    # Visualization
    fig, ax = plt.subplots()
    # length of x axis
    x = np.arange(0, data.maxlen, 1)
    line, = ax.plot(x, np.random.randint(-y_range *
                                         0.55, y_range*0.55, data.maxlen))
    plt.show(block=False)

    # Main loop
    while True:
        # Read microfone
        # raw (bytes)
        new_data = stream.read(CHUNK)
        # as int
        new_data = struct.unpack(str(CHUNK) + 'h', new_data)
        # add samples to buffer
        for sample in new_data:
            data.append(sample)

        mean = np.mean(np.abs(new_data))
        if mean > recording_amplitude_limit:
            logger.debug("recording amplitude reached")
            line.set_color('r')
        else:
            line.set_color('g')

        # visualization
        # line.set_ydata(np.array(data))
        # fig.canvas.draw()
        # fig.canvas.flush_events()

    # print("* recording")

    # frames = []

    # for i in range(0, int(RATE / CHUNK * 5)):
    #     data = stream.read(CHUNK)
    #     frames.append(data)

    # print("* done recording")

    # stream.stop_stream()
    # stream.close()
    # p.terminate()

    # wf = wave.open('test.wav', 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(b''.join(frames))
    # wf.close()


if __name__ == "__main__":
    logger = create_logger("recorder")
    args = parse_arguments()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("set verbose logging mode")

    main(args)

    exit(0)
