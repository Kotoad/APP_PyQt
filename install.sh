#!/bin/bash
APP_DIR="$HOME/.local/share/OmniBoardStudio"
ZIP_URL="https://github.com/Kotoad/APP_PyQt/releases/download/V0.11/OmniBoard.Studio.zip"

echo "Downloading OmniBoard Studio..."
wget -q --show-progress "$ZIP_URL" -O /tmp/omniboard.zip

echo "Extracting..."
mkdir -p "$APP_DIR"
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

# Ensure the executable has run permissions
chmod +x "$APP_DIR/OmniBoard Studio"
rm /tmp/omniboard.zip

echo "Installation complete. You can now launch OmniBoard Studio from your applications menu."