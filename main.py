import os
import argparse

from collections import deque

import cv2

arrow_keys = {
    'up': [82, 119],
    'down': [84, 115],
    'left': [81, 97],
    'right': [83, 100]
}

def generate_image_name(d, fe):
    for f in os.listdir(d):
        f = os.path.join(d, f)
        if os.path.isdir(f):
            yield from generate_image_name(f, fe)
        elif os.path.splitext(f)[-1] in fe:
            yield f

def read_line(line):
    image_label, image_name = line.split('|')
    return image_label, image_name[:-1]

def read_data(fname, data_queue, data_dict, flag='r'):
    if os.path.exists(fname):
        with open(fname, flag) as fhandle:
            line = fhandle.readline()
            while line:
                label, image_name = read_line(line)
                
                data_dict[image_name] = int(label)
                data_queue.append(image_name)

                line = fhandle.readline()
    return data_queue, data_dict

def write_line(image_name, image_label):
    return '{} |{}\n'.format(str(image_label), image_name)

def write_data(fname, data_dict, flag='w'):
    with open(fname, flag) as fwriter:
        for image_name, image_label in data_dict.items():
            fwriter.write(write_line(image_name, image_label))


def main(args):

    # Make sure extensions are valid format
    for i, ext in enumerate(args.ext):
        if ext[0] != '.':
            args.ext[i] = '.' + str(ext)

    # Folder will be the first positional argument
    args.folder = args.folder[0]

    # Assume fully specified path
    if os.path.isdir(os.path.abspath(args.folder)):
        args.folder = os.path.abspath(args.folder)
    # Assume the path is relative to the script
    elif os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), args.folder)):
        args.folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.folder)
    else:
        raise FileNotFoundError('Image folder does not exist')

    # Labels will be saved inside image directory (at the highest level)
    args.label = os.path.join(args.folder, args.label)

    print('Loading from folder: {}'.format(args.folder))
    print('Saving to labels file: {}'.format(args.label))

    if input('Are these file paths correct? (n for no)') == 'n':
        return
    
    data_queue = deque()
    data_dict = {}
    buffer_dict = {}

    # Update the dictionary with previous data
    data_queue, data_dict = read_data(args.label, data_queue, data_dict)

    # Update the dictionary with buffer data. This will only exist if the previous run crashed
    buffer_file = os.path.splitext(args.label)[0] + '_buffer.txt'
    if os.path.exists(buffer_file):
        print('Restoring labels from buffer file, do not close window')
        data_queue, data_dict = read_data(buffer_file, data_queue, data_dict)
        write_data(args.label, data_dict)

    index = len(data_queue)
    iteration = 0
    save_every = 20
    
    im_gen = generate_image_name(args.folder, args.ext)
    
    image_name = None
    while True:
        iteration += 1
        label = None

        # Grab a new image
        if index >= len(data_queue):
            try:
                image_name = next(im_gen)
                while image_name in data_dict:
                    image_name = next(im_gen)

                # Remove the abspath
                image_name = image_name.replace(args.folder, '')
            except StopIteration:

                # This will only happen if the image directory is empty
                if len(data_queue) == 0:
                    print('No images found, exiting')
                    return

                # Prevent from moving past the last image
                index -= 1
                continue
            data_queue.append(image_name)

            tag = 'Index: {}\t | Label: {}'.format(index, 'None')
        
        # Query an existing image
        else:

            # Prevent from moving past the first image
            if index == -1:
                index = 0
            image_name = data_queue[index]

            tag = 'Index: {}\t | Label: {}'.format(index, data_dict.get(image_name, 'None'))

        # Show the image
        print('Displaying image: {}'.format(image_name))
        print(tag)
        img = cv2.imread(args.folder + image_name)
        cv2.imshow('Image', img)

        # Get input from the user
        keypress = cv2.waitKey(0)
        if keypress in arrow_keys['up']:
            data_dict[image_name] = 1
            buffer_dict[image_name] = 1
            index += 1
        elif keypress in arrow_keys['down']:
            data_dict[image_name] = 0
            buffer_dict[image_name] = 0
            index += 1
        if keypress in arrow_keys['right']:
            index += 1
        elif keypress in arrow_keys['left']:
            index -= 1
        elif keypress == ord('q'):
            break
        
        tag = 'Index: {}\t | New Label: {}'.format(index-1, data_dict.get(image_name, 'None'))
        print(tag)

        # Save every once in a while
        if (iteration % save_every == 0) and iteration > 0:
            write_data(buffer_file, buffer_dict, flag='w+')
            buffer_dict = {}

    # Finally, write all data to the labels file
    print('Updating labels file, do not close the window')
    write_data(args.label, data_dict)

    # Clear the buffer file
    if os.path.exists(buffer_file):
        os.remove(buffer_file)

    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A sumer simple python tool to perform binary image classification using opencv.')
    parser.add_argument('folder', metavar='image folder', type=str, nargs=1,
                        help='path to highest level folder where images are located. \
                        Path can be relative to main script or an absolute path. \
                        Directory will be recursively explored when looking for \
                        images. ')
    parser.add_argument('--ext', '-e', metavar='extension', type=str, nargs='+', default=['.png'],
                        help='list of image extensions (file types) to look for. Supports \
                        those types supported by opencv: (bmp, pbm, pgm, ppm, sr, \
                        ras, jpeg, jpg, jpe, jp2, tiff, tif, png)')
    parser.add_argument('--label', '-l', metavar='label file', type=str, nargs=1, default='labels.txt',
                        help='resulting label file. Will be nested inside the image directory, \
                        at the highest level.')
    parser.add_argument('--save', '-s', metavar='save frequency', type=int, nargs=1, default=20,
                        help='how often to save buffered labels. The script will generate a \
                        temp file to persist labels in the event of a crash.')
    args = parser.parse_args()

    main(args)