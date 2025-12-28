
import os
from pathlib import Path

def load_token(path: str) -> str:
    token_file = Path(path)

    if not token_file.exists():
        raise FileNotFoundError('Token file not found : {}".'.format(path))

    try:
        st = token_file.stat()
        if st.st_mode & 0o077:
            print('The token file "{}" permission should be 600 (rw-------)'.format(path))
    except Exception:
        pass

    token = token_file.read_text(encoding="utf-8").strip()

    if not token:
        raise ValueError('The token file "{}" is empty.'.format(path))

    return token

