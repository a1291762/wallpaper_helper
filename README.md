Wallpaper Helper

This is an application to assist in cropping wallpaper for display on your monitor.


Dependencies

Ubuntu users should do apt-get install python3-pyside.

Mac users may be able to download and install something, but I found that I had to do things manually.

1) Install Qt 4 (may have to compile from source)
2) Install python 3.4
3) Download pyside 1.2.4
4) Run python3.4 setup.py build
4) Run python3.4 setup.py install


Installation

1) Run ./build to convert .ui files to python
2) Run ./wallpaper to start the program


Features

- Desktop size is detected (but can be manually set)
- Crop border is shown
- Position crop border using the mouse
- Resize crop border using + and - keys
- Arrow keys allow navigating all files in a folder
- Space toggles preview of the cropped image
- If an image exists in the originals directory, a * is displayed in the title bar
- Press O to toggle the original image


TODO

- One source image -> Two destination images
- Rotation of the destination image
- Allow the crop border to extend past the image boundaries (fill with a solid colour)
- Browse images from a new folder and copy to dest or crop to dest
- Remove the destination image, keep the original
- Original in a format other than JPG (output is always JPG)
- Port to pyside2 (Ubuntu has a snap, Mac users can download)
