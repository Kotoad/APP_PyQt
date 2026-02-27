#!/bin/bash
APP_DIR="$HOME/.local/share/OmniBoardStudio"
# Generic "latest" download URL for your repository
REPO="Kotoad/APP_PyQt"
URL="https://github.com/$REPO/releases/latest/download/OmniBoard_Studio_Linux.tar.gz"

echo "Downloading OmniBoard Studio..."
wget -q --show-progress "$URL" -O /tmp/omniboard.tar.gz

echo "Extracting..."
mkdir -p "$APP_DIR"
# Fixed: Now correctly extracts the .tar.gz file
tar -xzf /tmp/omniboard.tar.gz -C "$APP_DIR"

echo "Creating Application menu shortcut..."
mkdir -p "$HOME/.local/share/applications"
cat <<EOF > "$HOME/.local/share/applications/omniboard-studio.desktop"
[Desktop Entry]
Name=OmniBoard Studio
Exec="$APP_DIR/OmniBoard Studio"
Icon="$APP_DIR/resources/images/APPicon.ico"
Type=Application
Categories=Development;Electronics;
Terminal=false
EOF

chmod +x "$APP_DIR/OmniBoard Studio"
rm /tmp/omniboard.tar.gz

echo "Installation complete."