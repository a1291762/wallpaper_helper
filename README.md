# Wallpaper Helper

This is an application to assist in cropping wallpaper for display on your monitor.


# License

This source code is released under the MIT license (see LICENSE for details).


# Dependencies

PySide 6/Qt 6, PySide 2/Qt 5 or PySide/Qt 4


# Installation

1. Run ./build to convert .ui files to python (use -p pyside2 or -p pyside if
   using older than PySide 6)
2. Run ./wallpaper to start the program


# Features

- Desktop size is detected (can also be manually set)
- Crop border is shown
- Position crop border using the mouse (or shift + arrow for pixel-precise movement)
- Resize crop border using the scroll wheel (or + and - for pixel-precise sizing)
- Left/Right arrow keys allow navigating all files in a folder
- Space toggles cropped preview
- If an image is modified from the original, a * is displayed in the title bar
- Press O to toggle viewing the original image
- Original can be in a format other than .jpg (wallpaper is always .jpg)


# Workflow 1 - crop existing set of wallpapers

- Create empty folders for originals
- Set the wallpaper and originals paths in the app
- Drag an image from wallpaper folder onto the app
- Review images (left/right) and choose to save cropped (Control+S) versions as required
- Save uncropped (Control+R) versions to convert from non-JPEG to .jpg
- Choose to remove a wallpaper, moving the original (Backspace)


# Workflow 2 - add new images to wallpaper set

- Drag an image from proposed folder onto the app
- Review images (left/right) and choose to save original (Control+R) or cropped (Control+S) versions
- Choose to copy to originals folder, without adding to wallpaper (Backspace)


# Workflow 3 - review unused originals

- Drag an image from originals folder onto the app
- Toggle unused originals (Shift+O)
- Review images (left/right) and choose to save original (Control+R) or cropped (Control+S) versions


# TODO

- One original image -> two wallpaper images
- Rotate before crop
- Allow the crop border to extend past the image boundaries (fill with a solid colour)
- Packaging (installable package/app)
