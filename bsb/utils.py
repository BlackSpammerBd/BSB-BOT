# bsb/utils.py
def log_to_file(file_path, content):
    """
    Writes the given content to the specified file.
    """
    try:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"[UTILS] Logged data to {file_path}")
    except Exception as e:
        print(f"[UTILS] Error writing to file {file_path}: {e}")
