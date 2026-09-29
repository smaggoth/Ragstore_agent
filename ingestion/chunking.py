def chunck_markdown(files_path) -> list:
    """
    Function to divide document in chunks based on headers.
    Args:
        files_path: Path to markdown documents"""
    current_chunk = []
    chunks = []
    max_size = 800
    with open(files_path, "r", encoding='utf-8') as file:
        _list = file.readlines()
        lines = [line for line in _list if line != '\n']
        for line in lines:
            line = line.rstrip()

            if line.startswith('#') and not current_chunk:
                current_chunk.append(line)
            elif line.startswith('#') and current_chunk:
                chunk_temp  = '\n'.join(current_chunk)
                if len(chunk_temp) > max_size:
                    chunks.extend(sub_chunking(chunk_temp, max_size))
                else:
                    chunks.append(chunk_temp)
                current_chunk = []
                current_chunk.append(line)
            else:
                current_chunk.append(line)
        if current_chunk:
            chunk_temp  = '\n'.join(current_chunk)
            if len(chunk_temp) > max_size:
                chunks.extend(sub_chunking(chunk_temp, max_size))
            else:
                chunks.append(chunk_temp)
        return chunks

def sub_chunking(chunk, max_size=800):
    """Function to divide big chunks in smaller ones
    Args:
        chunk: Current big chunk to be divided.
        max_size: Maz size of the final little chunks"""
    lines = chunk.split('\n')
    sub_chunk = []
    actual = []
    actual_len = 0
    for line in lines:
        actual_len += len(line)
        if actual_len <= max_size:
            actual.append(line)
        else:
            if actual:
                sub_chunk.append('\n'.join(actual))

            if len(line) > max_size:
                extreme_chunk = [line[i:i+max_size] for i in range(0, len(line), max_size)]
                sub_chunk.extend(extreme_chunk)
                actual = []
                actual_len = 0
            else:
                actual = [line]
                actual_len = len(line)

    if actual:
        sub_chunk.append('\n'.join(actual))
    return sub_chunk
        

if __name__ == '__main__':
    from pathlib import Path
    result = sub_chunking('# Proyecto RAG con Agentes Orquestados')
    print(len(result))
    #files_path = Path(__file__).resolve().parent.parent/ "docs" / "README.md"
    #chunks = chunck_markdown(files_path)
    #print(len(chunks))
   