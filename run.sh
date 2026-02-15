#!/bin/bash

# Get the directory where this script actually lives
# This ensures it finds the .venv even if you call the script from a subfolder
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment using the absolute path
source "$SCRIPT_DIR/.venv/bin/activate"
echo "Env activated, running manim..."

# Check if a file argument is provided
if [ -z "$1" ]; then
  echo "Usage: ./run.sh path/to/script.py [SceneName]"
  # Added -p to the suggestion so it auto-plays
  echo "Example: ./run.sh linear/linear_transform.py EigenvectorTransformation" 
  exit 1
fi

SCRIPT=$1
SCENE=$2

# Run manim
# Added -p (Preview/Play) so the video opens automatically
manim -pql "$SCRIPT" "$SCENE"