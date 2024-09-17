import os

def is_text_file(file_path, blocksize=512):
    """
    Determines if a file is a text file.
    Tries to read a block of the file and checks for decoding errors.
    """
    try:
        with open(file_path, 'rb') as file:
            block = file.read(blocksize)
            if b'\0' in block:
                return False
            # Try decoding to UTF-8
            block.decode('utf-8')
            return True
    except:
        return False

def consolidate_files(directory, output_file):
    """
    Consolidates all text files in the specified directory into a single text file.
    
    Args:
    - directory (str): Path to the directory containing the files.
    - output_file (str): Path to the output consolidated text file.
    """
    # Get a list of all files in the directory
    files = os.listdir(directory)
    
    # Sort files for consistent ordering
    files.sort()
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in files:
            file_path = os.path.join(directory, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check if the file is a text file
            if not is_text_file(file_path):
                print(f"Skipping non-text file: {filename}")
                continue
            
            # Write the header
            outfile.write(f"#####################\n{filename}\n#####################\n")
            
            # Read and write the file content
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content + "\n\n")  # Add spacing between files
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    print(f"All files have been consolidated into '{output_file}'.")

if __name__ == "__main__":
    import argparse

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Consolidate all text files in a directory into a single text file.")
    parser.add_argument(
        "-d", "--directory",
        type=str,
        default=".",
        help="Path to the directory containing the files. Defaults to the current directory."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="consolidated_files.txt",
        help="Name of the output file. Defaults to 'consolidated_files.txt'."
    )

    args = parser.parse_args()

    # Get absolute paths
    directory = os.path.abspath(args.directory)
    output_file = os.path.abspath(args.output)

    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        exit(1)

    consolidate_files(directory, output_file)
