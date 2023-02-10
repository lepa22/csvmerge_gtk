#!/bin/bash

echo "Installing dependencies using pip..."
pip install .
echo "Dependencies installed."
sleep 1
echo
echo "Copying application icon to ~/.icons..."
mkdir ~/.icons
cp ./csvmerge_icon_128.png ~/.icons
echo "Application icon copied."
echo "Adding application to ~/.local/share/applications..."
cp ./csvmerge_gtk.desktop ~/.local/share/applications
echo "Application added."
