from pylsl import StreamInfo, StreamOutlet
import re
from time import sleep


def main():
    data = open('meditation.txt').readlines()
    info = StreamInfo('OpenBCI', 'EEG', 8, 256, 'float32', 'rp36o')
    outlet = StreamOutlet(info)
    for line in data:
        if re.search(r'^\d', line):
            sample = [float(e[1:]) for e in line.split(',')[1:9]]
            outlet.push_sample(sample)
            sleep(1 / 256)


if __name__ == "__main__":
    main()