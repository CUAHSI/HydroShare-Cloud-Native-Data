#!/bin/bash

TAG=latest
if [ $# -eq 0 ]; then
	echo "No image TAG supplied"
	echo
	echo "Usage: $0 <TAG>"
	echo
	read -p "Do you want to continue with TAG = 'latest'? [Y/n] " -n 1 -r
	if [[ $REPLY =~ ^[Nn]$ ]]; then
		echo
		echo Exiting...
		exit 1
	fi
else
	TAG=$1
fi

print_box() {
	local block_text="$1"
	local text_width=${#block_text}
	local line_width=$((text_width + 4)) # 2 hyphens and 2 spaces on each side

	# Print the top line with rounded corners
	printf "╭%*s╮\n" "$line_width" | tr ' ' '─'

	# Print the block text surrounded by spaces
	printf "│  %s  │\n" "$block_text"

	# Print the bottom line with rounded corners
	printf "╰%*s╯\n" "$line_width" | tr ' ' '─'
}

msg="Building cuahsi/cfe-configure:$TAG"
print_box "$msg"

docker build -f Dockerfile -t cuahsi/cfe-configure:$TAG ../

print_box "Build Complete!"
