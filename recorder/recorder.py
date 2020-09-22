from utils.logger import create_logger
from utils.parser import parse_arguments
import wave
import logging
import collections
import pyaudio
import struct
import datetime
import os
import numpy as np


# Buffer size in sec (pre recording)
RECORD_BUFFER_SIZE = 3

# Decay time, post record in sec
DECAY_TIME = 3

# Threshold when amplitude is high (% of max amplitude)
RECORD_THRESHOLD = 0.015

# output dir:
OUTPUT_PATH = "output"


def save_recording(pyaudio_obj, channels, format, rate, data):
    # create output path
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    # filename
    filename = os.path.join(OUTPUT_PATH, datetime.datetime.now().replace(
        microsecond=0).isoformat() + ".wave")
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio_obj.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(data))
        wf.close()
        logger.info("Written file %s" % filename)


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
    # pyaudio object
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
    pre_record_buf = collections.deque(
        maxlen=int(RATE/CHUNK * RECORD_BUFFER_SIZE))

    # pre record buffer - for visualization (filled with ints not byte data)
    pre_record_buf_int = collections.deque(
        maxlen=int(RATE * RECORD_BUFFER_SIZE))
    # fill with zeros
    for _ in range(pre_record_buf_int.maxlen):
        pre_record_buf_int.append(0)

    # preprocess absolute amplitude threshold
    recording_amplitude_limit = (y_range / 2) * RECORD_THRESHOLD

    # colddown chunks, numberof chunks after last activation before stopping recording.
    decay_chunks = DECAY_TIME * RATE/CHUNK

    # recording flag
    is_recording = False

    # recorded_data, holding recorded data before writing in to file.
    recorded_data = []

    # record counter
    counter = decay_chunks

    # Visualization
    if args.plot:
        fig, ax = plt.subplots()
        # length of x axis
        x = np.arange(0, pre_record_buf_int.maxlen, 1)
        line, = ax.plot(x, np.random.randint(-y_range *
                                             0.55, y_range*0.55, pre_record_buf_int.maxlen))
        plt.show(block=False)

    # Main loop
    while True:
        # Read microfone
        # raw (bytes)
        new_data = stream.read(CHUNK)
        # as int
        new_data_int = struct.unpack(str(CHUNK) + 'h', new_data)

        # decide to start to record
        mean = np.mean(np.abs(new_data_int))
        if mean > recording_amplitude_limit:
            logger.debug("recording amplitude reached")
            counter = decay_chunks
            if not is_recording:
                logger.info("Start new recording")
                recorded_data = []
                is_recording = True
                for sample in pre_record_buf:
                    recorded_data.append(sample)

        # append new data to recording
        if is_recording:
            logger.info("recording... chunks to go %i" % counter)
            counter -= 1
            recorded_data.append(new_data)
            if counter <= 0:
                logger.info("done recording")
                is_recording = False
                save_recording(p, CHANNELS, FORMAT, RATE, recorded_data)

        # append new data pre record buffer
        pre_record_buf.append(new_data)

        # visualization
        if args.plot:
            # append latest data
            for sample in new_data_int:
                pre_record_buf_int.append(sample)
            # set y data
            line.set_ydata(np.array(pre_record_buf_int))
            # set line color
            if is_recording:
                line.set_color('r')
            else:
                line.set_color('g')
            # update graph
            fig.canvas.draw()
            fig.canvas.flush_events()


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
