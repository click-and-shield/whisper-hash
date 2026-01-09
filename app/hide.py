# Usage:
#
#   DRY-RUM:
#      python hide.py --debug --dry-run --verbose --token /home/dev/.token ../test-data/config.yaml secret-key ../test-data/needle.txt ../test-data/haystack.txt output.txt
#   NORMAL-RUN:
#      python hide.py --debug --verbose --token /home/dev/.token ../test-data/config.yaml secret-key ../test-data/needle.txt ../test-data/haystack.txt output.txt

from typing import Optional
import argparse
from pathlib import Path
import shutil
import sys
import os



CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
print("Set search path: {}".format(SEARCH_PATH))
sys.path.insert(0, SEARCH_PATH)

from whisper.whisperer import Whisperer, Params
from whisper.config import Config, load_config
import whisper.api_tools

def get_script_dir() -> Path:
    """Returns the path to the directory containing the script."""
    return Path(__file__).resolve().parent

def init_env(debug_path: Optional[Path]) -> None:
    if debug_path is None:
        return
    if debug_path.exists():
        for child in debug_path.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)
    else:
        debug_path.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    script_dir: Path = get_script_dir()
    default_debug_path: str = script_dir.joinpath("debug").__str__()
    default_tokens_path: str = script_dir.joinpath(".token").__str__()
    default_model: str = 'gpt-5.1'

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Hide a text file within a generated text file.')
    parser.add_argument('--verbose',
                        dest='verbose_flag',
                        action='store_true',
                        help='activate verbose output')
    parser.add_argument('--dry-run',
                        dest='dry_run_flag',
                        action='store_true',
                        help='dry-run flag')
    parser.add_argument('--debug',
                        dest='debug_flag',
                        action='store_true',
                        help='debug flag')
    parser.add_argument('--debug-dir',
                        dest='debug_dir',
                        type=str,
                        required=False,
                        default=default_debug_path,
                        help='path to the directory used to store DEBUG data (default: "{}")'.format(default_debug_path))
    parser.add_argument('--token',
                        dest='token',
                        type=str,
                        required=False,
                        default=default_tokens_path,
                        help='path to the file containing the token to use for ChatGPT API (default: "{}")'.format(default_tokens_path))
    parser.add_argument('config',
                        type=str,
                        help='path to the YAML configuration file')
    parser.add_argument('key',
                        type=str,
                        help='secret key to use for hiding the text file')
    parser.add_argument('needle',
                        type=str,
                        help='path to the text file to hide')
    parser.add_argument('haystack',
                        type=str,
                        help='path to the text file used as a "haystack" for hiding')
    parser.add_argument('output',
                        type=str,
                        help='path to the output file')

    args = parser.parse_args()
    verbose_flag: bool = args.verbose_flag
    dry_run_flag: bool = args.dry_run_flag
    debug_flag: bool = args.debug_flag
    debug_dir: str = args.debug_dir
    config_path: str = args.config
    key: str = args.key
    needle_path: str = args.needle
    haystack_path: str = args.haystack
    output_path: str = args.output
    token_path: str = args.token

    # Load the API token
    try:
        token: str = whisper.api_tools.load_token(token_path)
    except Exception as e:
        print('Error loading token file "{}": {}'.format(token_path, str(e)))
        exit(1)

    # Load the configuration
    try:
        config: Config = load_config(config_path)
    except Exception as e:
        print('Error loading configuration file "{}": {}'.format(config_path, str(e)))
        exit(1)


    # Initialize the environment
    init_env(Path(debug_dir))

    try:
        params: Params = Params(token, debug_dir if debug_flag else None, verbose_flag, dry_run_flag)
        w: Whisperer = Whisperer(params, config)
    except ValueError as e:
        print('Error initializing Whisperer: {}'.format(str(e)))
        exit(1)
    w.hide(needle_path, haystack_path, key, output_path)



