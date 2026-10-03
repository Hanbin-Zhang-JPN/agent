#!/bin/zsh
set -euo pipefail

cd "${0:A:h}"
app="${PWD}/build/DiskWatch.app"
sdk="$(xcrun --show-sdk-path)"
# Some Command Line Tools installations ship a newer SDK than their Swift compiler.
if [[ -d /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk ]]; then
  sdk=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk
fi
mkdir -p "$app/Contents/MacOS" build/module-cache
CLANG_MODULE_CACHE_PATH="$PWD/build/module-cache" swiftc \
  -sdk "$sdk" -target arm64-apple-macosx14.0 -O \
  -framework SwiftUI -framework IOKit \
  Sources/DiskProbe.swift Sources/DiskWatchApp.swift \
  -o "$app/Contents/MacOS/DiskWatch"
cp Info.plist "$app/Contents/Info.plist"
echo "Built $app"
