#mport matplotlib.pyplot as plt
from datetime import datetime
import serial
import struct
import math
import os
import time

# Show all packets
VERBOSE = 0

# Native USB port of Due (use Device Manager to find)
SONAR_PORT = 'COM4'
ROTATION_PORT = 'COM13'

def read(ser, n):
    data = ser.read(size=n)
    if VERBOSE:
        print('> ' + ''.join('{:02x} '.format(b) for b in data))
    return data


def write(ser, data):
    ser.write(bytearray(data))
    if VERBOSE:
        print('< ' + ''.join('{:02x} '.format(b) for b in data))


def main():
    # Open connection to device
    ser = serial.Serial()
    ser.port = SONAR_PORT
    ser.baudrate = 115200  # arbitrary
    ser.setRTS(True)
    ser.setDTR(True)
    ser.open()

    ser_rotation = serial.Serial()
    ser_rotation.port = ROTATION_PORT
    ser_rotation.baudrate = 115200  # arbitrary
    ser_rotation.setRTS(True)
    ser_rotation.setDTR(True)
    ser_rotation.open()

    print('Communicating over port {}'.format(ser.name))

    # Send handshake to device
    write(ser, [0, 0, 0, 0, 0])
    opcode, response_len = struct.unpack('<BI', read(ser, 5))
    if opcode != 0x80 or response_len != 2:
        print('Unexpected packet! opcode=0x{:02x}, response_len={}'
              .format(opcode, response_len))
        return

    version = struct.unpack('<BB', read(ser, response_len))
    print('Connected to device (version {})'.format(version))

    # Ask for name of output folder
    print('Enter name of folder: ', end='')
    folder_name = input()

    use_dynamic_motion = False
    rotation_angle = 0
    sample_id = 0

    while True:
        try:
            # Rotate one step (1.8deg)
            for i in range (0, 100):
                write(ser_rotation, [2, 0])
            rotation_angle = rotation_angle + 1.8
            sample_id = sample_id + 1

            time.sleep(1)
            # Initiate data collection
            collection_opcode = 3 if use_dynamic_motion else 2
            write(ser, [collection_opcode, 0, 0, 0, 0])
            opcode, response_len = struct.unpack('<BI', read(ser, 5))
            if opcode != (0x80 | collection_opcode) or response_len != 0:
                print('Unexpected packet! opcode=0x{:02x}, response_len={}'
                      .format(opcode, response_len))
                return

            print('Collecting data... ', end='')

            # Wait for data collection to finish
            opcode, response_len = struct.unpack('<BI', read(ser, 5))
            if opcode != 0x82:
                print('Unexpected packet! opcode=0x{:02x}, response_len={}'
                      .format(opcode, response_len))
                return

            print('done! ({} data points)'.format(response_len // 2))

            # Create output folder and file
            output_folder = folder_name + '/' + ('dynamic' if use_dynamic_motion else 'static')
            output_filename = 'sample_' + str(sample_id) + '_rotation_angle_' + "{0:.2f}".format(rotation_angle) + '.txt'

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Transfer the data over
            raw_data = read(ser, response_len)
            parsed_data = []
            with open(output_folder + '/' + output_filename, 'w') as f:
                for i in range(0, len(raw_data), 2):
                    data = raw_data[i] | (raw_data[i + 1] << 8)
                    parsed_data.append(data)
                    f.write('{}\n'.format(data))

        except KeyboardInterrupt:
            break

    print('Closing connection')
    ser.close()


if __name__ == '__main__':
    main()