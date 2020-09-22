from utils.logger import create_logger
from utils.parser import parse_arguments
import wave
import logging
import collections
import pyaudio
import struct
import time
import numpy as np


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

    # preRecord Buffer - Ring buffer
    pre_record_buf = collections.deque(maxlen=RATE * RECORD_BUFFER_SIZE)
    # fill with zeros
    for _ in range(pre_record_buf.maxlen):
        pre_record_buf.append(0)

    # preprocess absolute amplitude threshold
    recording_amplitude_limit = (y_range / 2) * RECORD_THRESHOLD

    # recording flag
    is_recording = False

    # recorded_data, holding recorded data before writing in to file. 
    recorded_data = []

    # record counter
    counter = 0

    # Visualization
    if args.plot:
        fig, ax = plt.subplots()
        # length of x axis
        x = np.arange(0, pre_record_buf.maxlen, 1)
        line, = ax.plot(x, np.random.randint(-y_range *
                                            0.55, y_range*0.55, pre_record_buf.maxlen))
        plt.show(block=False)

    # Main loop
    while True:
        ## Read microfone
        # raw (bytes)
        new_data = stream.read(CHUNK)
        # as int
        new_data = struct.unpack(str(CHUNK) + 'h', new_data)

        # decide to start to record
        mean = np.mean(np.abs(new_data))
        if mean > recording_amplitude_limit:
            logger.debug("recording amplitude reached")
            if not is_recording:
                logger.info("Start new recording")
                recorded_data = []
                counter = 0
                is_recording = True
                recorded_data

        # append new data to recording
        if is_recording:
            logger.info("recording...")
            counter += 1
            recorded_data.append(new_data)
            if counter > 100:
                is_recording = False
                save_recording(recorded_data)
            
        # append new data pre record buffer
        for sample in new_data:
            pre_record_buf.append(sample)

        # visualization
        if args.plot:
            line.set_ydata(np.array(pre_record_buf))
            fig.canvas.draw()
            fig.canvas.flush_events()
            #TODO depend on recording state 
            if mean > recording_amplitude_limit:
                line.set_color('r')
            else:
                line.set_color('g')

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

    if args.plot:
        import matplotlib
        matplotlib.use('TKAgg')
        import matplotlib.pyplot as plt

    main(args)

    exit(0)
