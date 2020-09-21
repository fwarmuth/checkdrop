import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import collections


# change matplot lib backend
matplotlib.use('TKAgg')


# Audio chunk, samples per frame
CHUNK = 1024 * 4
# sample format
FORMAT = pyaudio.paInt16
#Mono
CHANNELS = 1
# samples per secound
RATE = 44100

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
line, = ax.plot(x, np.random.randint(-2**15, 2**15, CHUNK*5))

plt.show(block=False)
while True:
    # raw (bytes)
    new_data = stream.read(CHUNK)
    # as int
    new_data  = struct.unpack(str(CHUNK) + 'h', new_data)

    # add sample to buffer
    for sample in new_data:
        data.append(sample)

    line.set_ydata(np.array(data))

    fig.canvas.draw()
    fig.canvas.flush_events()

