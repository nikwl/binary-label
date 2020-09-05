# binary-label

## Overview

A sumer simple python tool to perform binary image classification. Install required packages and then run `python main.py <folder>` to start classifying. Modify the code to add more classification categories, or just use as is. 

# Installation

1. Install required packages (opencv):
	```bash
	pip install -r requirements.txt
	```

2. Test installation:
	```bash
	python main.py <folder>
	```

# Instructions

Run `main.py -h` for a list of required and optional arguments.  

```bash
positional arguments:
  image folder          path to highest level folder where images are located.
                        Path can be relative to main script or an absolute
                        path. Directory will be recursively explored when
                        looking for images.

optional arguments:
  -h, --help            show this help message and exit
  --ext extension [extension ...], -e extension [extension ...]
                        list of image extensions (file types) to look for.
                        Supports those types supported by opencv: (bmp, pbm,
                        pgm, ppm, sr, ras, jpeg, jpg, jpe, jp2, tiff, tif,
                        png)
  --label label file, -l label file
                        resulting label file. Will be nested inside the image
                        directory, at the highest level.
  --save save frequency, -s save frequency
                        how often to save buffered labels. The script will
                        generate a temp file to persist labels in the event of
                        a crash.
```