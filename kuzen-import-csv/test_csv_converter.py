#!/usr/bin/env python3
"""
Test script for csv_cp932_converter.py

Usage:
    python test_csv_converter.py <input_file> [--output <output_file>]

Example:
    python test_csv_converter.py sample.csv
    python test_csv_converter.py sample.csv --output converted_sample.csv
"""

import subprocess
import sys
import os

def main():
    # Check if at least one argument is provided
    if len(sys.argv) < 2:
        print("Error: Input file is required.")
        print("Usage: python test_csv_converter.py <input_file> [--output <output_file>]")
        sys.exit(1)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the command to run csv_cp932_converter.py
    cmd = ["python", os.path.join(script_dir, "csv_cp932_converter.py")]
    
    # Add all arguments passed to this script
    cmd.extend(sys.argv[1:])
    
    # Print the command being executed
    print(f"Executing: {' '.join(cmd)}")
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Conversion completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()