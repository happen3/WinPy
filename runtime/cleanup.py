import os

# Define the directory to clean (current directory by default)
directory = '.'

# List of extensions and filenames to keep
extensions_to_keep = ['.reg', '.py', ".bat"]
filenames_to_keep = ["nsodfnkhkqqfbqshfqsfgqsfhhqsfkqjsdfqdsg.ddsghqisfygsyfgsqufsukgd", 'requirements', ".gitignore"]

# Iterate over all files in the directory
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)

    # Check if it's a file (not a directory)
    if os.path.isfile(filepath):
        # Get file extension and name
        _, ext = os.path.splitext(filename)
        name, _ = os.path.splitext(filename)

        # Determine if the file should be deleted
        if ext.lower() not in extensions_to_keep and name not in filenames_to_keep:
            print(f"Deleting {filepath}")
            os.remove(filepath)