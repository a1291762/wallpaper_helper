# Wallpaper Helper

This is an application to assist in cropping wallpaper for display on your monitor.


# Dependencies

## Ubuntu

    sudo apt-get install python3-pyside

## Mac

There are binary packages but I found that they did not work.

1. Install Qt 4 (I compiled from source, this may be required)
2. Install python 3.4
3. Download pyside 1.2.4 (to a location it can permanently live)
4. Run python3.4 setup.py build
5. Run python3.4 setup.py install


# Installation

1. Run ./build to convert .ui files to python
2. Run ./wallpaper to start the program


# Features

- Desktop size is detected (can also be manually set)
- Crop border is shown
- Position crop border using the mouse (or shift + arrow for pixel-precise movement)
- Resize crop border using the scroll wheel (or + and - for pixel-precise sizing)
- Left/Right arrow keys allow navigating all files in a folder
- Space toggles preview of the cropped image
- If the same image exists in the originals directory, a * is displayed in the title bar
- Press O to toggle the original image
- Original can be in a format other than JPG (wallpaper is always JPG)


# TODO

- Keep all originals in originals, copy/link to wallpaper
- One original image -> two wallpaper images
- Rotate before crop
- Allow the crop border to extend past the image boundaries (fill with a solid colour)
- Browse images from a new folder and copy to wallpaper (can already crop to wallpaper/save to originals)
- Remove the wallpaper image, keep the original
- Port to pyside2 (Ubuntu has a snap, Mac users can download)
- Packaging (installable package/app)
