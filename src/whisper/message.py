# Usage:
#   python3 ../src/whisper/message.py ../test-data/needle.txt vector.txt


from typing import cast

if __name__ == '__main__':
    import sys
    import os
    CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
    SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir))
    sys.path.insert(0, SEARCH_PATH)
    from whisper.conversion import Conversion
    from whisper.types import Int64, Vector
else:
    from .conversion import Conversion
    from .types import Int64, Int16, Vector

class Message:

    @staticmethod
    def string_to_vector(s: str, length: int = 64) -> Vector:
        """Convert a string to a vector.
        The vector is a list of bits, where the first 64 bits are the length of the string,
        And the remaining bits are the string.
        """
        v_length: Vector = []
        if length == 64:
            v_length = Conversion.int64_to_bit_list(cast(Int64, len(s)))
        elif length == 16:
            v_length = Conversion.int16_to_bit_list(cast(Int16, len(s)))
        else:
            raise ValueError("Invalid length for string to vector conversion: {} (must be 64 or 16).".format(length))

        body = Conversion.bytes_to_bit_list(s.encode("ascii"))
        return v_length + body

    @staticmethod
    def load_text_file(file_path: str) -> str:
        """
        Loads a text file encoded in ASCII.

        Args:
            file_path (str): Path to the file to load.

        Returns:
            str: Content of the file.

        Raises:
            Exception: If the file cannot be read or decoded.
        """
        try:
            with open(file_path, "r", encoding="ascii") as f:
                return f.read()
        except UnicodeDecodeError as e:
            raise ValueError("Invalid encoding for file '{}'.".format(file_path)) from e

    @staticmethod
    def load_text_file_as_vector(file_path: str, length: int = 64) -> Vector:
        """
        Loads the content of a text file and converts it into a Vector representation.

        This function first reads the entire content of the file specified by `file_path`
        as a string, and then transforms that string into a Vector object.

        Args:
            file_path (str): The path to the text file to be loaded.
            length (int): The number of bits used to represent the number of bits of the texte file.
                          Defaults to 64.

        Returns:
            Vector: A vector representation of the text file's content.

        Raises:
            FileNotFoundError: If the file at `file_path` does not exist.
            IOError: If an error occurs while reading the file.
        """
        text = Message.load_text_file(file_path)
        return Message.string_to_vector(text, length)


if __name__ == '__main__':
    import argparse

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Convert a text file to a vector representation.')
    parser.add_argument('input',
                        type=str,
                        help='path to the input file')
    parser.add_argument('output',
                        type=str,
                        help='path to the output file')

    args = parser.parse_args()
    input_path: str = args.input
    output_path: str = args.output
    vector: Vector = Message.load_text_file_as_vector(input_path)
    with open(output_path, 'w') as f:
        f.write('vector: {}\n'.format(str(vector)))
        f.write('\n')
        f.write('length: {}\n'.format(str(vector[:64])))
        f.write('\n')
        for i in range(64, len(vector), 8):
            bits = vector[i:i+8]
            f.write('byte %-4s: %s %s\n' % (i//8, str(bits), Conversion.bit_list_to_bytes(bits).__str__()))


