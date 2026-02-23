# Create a new file (overwrites if exists)
with open("example.txt", "w") as file:
    file.write("Hello, this is my first file!")

# Create file only if it doesn't exist
with open("unique_file.txt", "x") as file:
    file.write("This file will only be created if it doesn't exist")

# Create and append to file
with open("log.py", "a") as file:
    file.write("New log entry\n")
