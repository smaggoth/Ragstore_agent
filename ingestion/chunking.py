def chunck_markdown(files_path):
    """
    Function to divide document in chunks based on headers.
    Ars:
        files_path: Path to markdown documents"""
    current_chunk = []
    chunks = []
    with open(files_path, "r", encoding='utf-8') as file:
        _list = file.readlines()
        lines = [line for line in _list if line != '\n']
        for line in lines:
            line = line.rstrip()

            if line.startswith('#') and not current_chunk:
                current_chunk.append(line)
            elif line.startswith('#') and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_chunk.append(line)
            else:
                current_chunk.append(line)
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        print(chunks)
        return chunks