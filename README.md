# Personal Media Manager

Personal Media Manager is a desktop application built with Python and PyQt5 that helps you organize, search, and manage your image and video collections. It provides a visual folder browser, thumbnail previews, duplicate image detection, sorting capabilities, and a soft-deletion recycling system.

## Features

- **Visual Folder Navigator**: A file system directory tree that lets you easily browse your local drives.
- **Thumbnail Previews**: Supports image thumbnails (.jpg, .jpeg, .png) and generates video frame previews (.mp4, .mov, .avi) using OpenCV.
- **Search & Filter**: Search files dynamically in the current directory by typing keywords into the search bar.
- **Perceptual Duplicate Detection**: Scans the current folder to identify visually identical or highly similar images using average hashing (via the `imagehash` library).
- **Soft Deletion & Recycle Bin**: Deleting media files moves them to a local `.recycle_bin` directory, enabling you to undo the deletion and restore files to their original location.
- **Flexible Sorting & View Modes**: Sort by name or modification date (ascending/descending) and adjust icon sizing (extra large, large, medium, small, list, details).
- **Drag and Drop Support**: Drag folders directly onto the interface to open and view their contents.

## Tech Stack

- **GUI Framework**: PyQt5
- **Image Processing**: Pillow (PIL) and OpenCV
- **Duplicate Analysis**: imagehash

## Requirements

Ensure you have Python 3.x installed along with the required libraries:

```bash
pip install PyQt5 Pillow opencv-python imagehash
```

## Running the Application

To start the media manager, run the following command:

```bash
python app.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.