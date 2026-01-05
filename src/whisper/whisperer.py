import json
from typing import Optional
from pathlib import Path
from .hasher import Hasher
from .types import Vector, MessageType, Role
from .chat_gpt import ChatGPT
from .stegano_db import SteganoDb
from .text_file_tool import read_sections_from_file
import whisper.message
from dataclasses import dataclass

@dataclass
class Params:
    model: str = None
    token: str = None
    debug_path: Optional[str] = None
    verbose: bool = False
    dry_run: bool = False

REQ_TEMPERATURE: float = 0.7

REQ_SYSTEM: str = """
Tu es un écrivain professionnel.
À chaque demande de reformulation, propose une version différente des précédentes,
en variant le vocabulaire et la structure des phrases, tout en conservant fidèlement le sens.

1. La sortie finale doit être STRICTEMENT un JSON valide:

   {
      "result": "..."
   }
 
2. Aucun commentaire, aucun texte explicatif, aucun Markdown, aucun texte supplémentaire.
"""


class Message:
    """Implementation of the OpenAI ChatCompletion API message format.
    This message is characterized by its role its type:
    - SYSTEM: this type of message is associated with the "system" role.
              See the OpenAI documentation for more information.
    - ASSISTANT: this type of message is associated with the "assistant" role.
                 See the OpenAI documentation for more information.
    - USER: this type of message is associated with the "user" role.
            See the OpenAI documentation for more information.
    - USER_INIT: this type of message is associated with the "user" role.
                 There is only one USER_INIT message per request.
                 This message is sent before the first message is type "USER".
    - USER_TERMINAL: this type of message is associated with the "user" role.
                     There is only one USER_INIT message per request.
                     This message is sent after the last message is type "USER".
    """

    def __init__(self, message_type: MessageType, content: str) -> None:
        self.content: str = content
        if message_type == MessageType.SYSTEM:
            self.role: Role = Role.SYSTEM
        elif message_type == MessageType.USER_INIT or message_type == MessageType.USER_TERMINAL:
            self.role: Role = Role.USER
        elif message_type == MessageType.USER:
            self.role: Role = Role.USER
        elif message_type == MessageType.ASSISTANT:
            self.role: Role = Role.ASSISTANT
        else:
            raise ValueError("Invalid message type: {}".format(message_type))

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role.value, 'content': self.content}

class Request:

    def __init__(self, messages: list[Message]) -> None:
        self.messages: list[Message] = messages

    def to_dict(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for message in self.messages:
            result.append(message.to_dict())
        return result


class Whisperer:

    def __init__(self, params: Params, db_path: Optional[str]=None) -> None:
        """Initializes the Whisperer.
        The parameters are:
          - model: the model to use for the LLM. Set to None for testing using the dry-run mode.
          - token: the token to use for the LLM. Set to None for testing using the dry-run mode.
          - debug_path: the path to the directory where the debug files will be stored.
          - verbose: whether to print verbose output.
          - dry_run: whether to use the dry-run mode.

        Note: the parameter "debug_path" is only used for DEBUG purposes.
        """
        # Sanity checks.
        self.chat_gpt: ChatGPT = ChatGPT(params.model, params.token)
        self.debug_path: Optional[Path] = Path(params.debug_path) if params.debug_path is not None else None
        self.params: Params = params
        self.call_count: int = 0

        # Create or open the database.
        if db_path is None:
            stegano_db_path: Optional[Path] = None
            if self.debug_path is not None:
                stegano_db_path = self.debug_path.joinpath('stegano-db.sqlite')
            self.db: SteganoDb = SteganoDb(stegano_db_path.__str__() if stegano_db_path is not None else None)
        else:
            self.db: SteganoDb = SteganoDb(db_path, init=False)

    @staticmethod
    def generate_single_message_request(text: str) -> Request:
        messages: list[Message] = [
            Message(MessageType.SYSTEM, REQ_SYSTEM),
            Message(MessageType.USER, text)
        ]
        return Request(messages)

    def save_request_for_debug(self, request: Request, call_count: int) -> None:
        if self.debug_path is None:
            return
        debug_path: Path = self.debug_path.joinpath('request-{}.json'.format(call_count))
        print("=> {}".format(debug_path))
        with open(debug_path, 'w') as f:
            f.write('REQUEST:\n\n')
            f.write(json.dumps(request.to_dict(), indent=2, ensure_ascii=False))

    def save_response_for_debug(self, response: str,  call_count: int) -> None:
        if self.debug_path is None:
            return
        debug_path: Path = self.debug_path.joinpath('request-{}.json'.format(call_count))
        with open(debug_path, 'a') as f:
            f.write('\n\nRESPONSE:\n\n')
            f.write(json.dumps(response, indent=2, ensure_ascii=False))

    def exec_request(self, request: Request) -> str:
        self.save_request_for_debug(request, self.call_count)
        d: list[dict[str, str]] = request.to_dict()
        try:
            response: str = self.chat_gpt.call(d)
        except Exception as e:
            raise RuntimeError("Error calling the LLM: {}".format(str(e)))
        self.save_response_for_debug(response, self.call_count)
        result: str = json.loads(response)['result']
        self.call_count += 1
        return result

    def hide(self, needle: str, haystack: str, secret_key: str, output_path: str) -> None:
        # Load the input text.
        position: int = 0
        for section in read_sections_from_file(haystack):
            self.db.add_original_text(position, section)
            position += 1

        # Load the message to hide.
        m: Vector = whisper.message.Message.load_text_file_as_vector(needle)
        position: int = 0
        for b in m:
            self.db.set_expected_bit(position, b)
            position += 1

        # Sanity checks.
        if len(m) > len(self.db):
            raise ValueError('The message to hide ({}) is too long (needs {} text sections, but if haystack "{}" is only {} text sections)'.format(needle, len(m), haystack, len(self.db)))

        # Initialize the hasher.
        hasher: Hasher = Hasher(secret_key)

        # Call the LLM.
        for section in self.db.get_sections():
            algorithm: str = hasher.next_hash_algorithm()
            _, bit = hasher.get_parity(algorithm, section.original_text)

            if section.expected_bit is None or bit == section.expected_bit:
                # The original text section is already suitable for the expected bit, or is an extra text section.
                self.db.set_traduction(section.position, section.original_text)
                if self.params.verbose:
                    if section.expected_bit is None:
                        print("%-3d: - -> reminder" % section.position)
                    else:
                        print("%-3d: %d -> %s" % (section.position, section.expected_bit, "OK"))
                continue

            if self.params.verbose:
                print("%-3d: %d -> need reformulation " % (section.position, section.expected_bit), end='')

            # The original text is not suitable for the expected bit. It needs to be reformatted.
            while True:
                if self.params.verbose:
                    print(".", end='', flush=True)
                request: Request = self.generate_single_message_request(section.original_text)
                if self.debug_path is not None:
                    self.save_request_for_debug(request, self.call_count)

                if self.params.dry_run:
                    self.call_count += 1
                    break

                traduction: str = self.exec_request(request)
                _, bit = hasher.get_parity(algorithm, traduction)
                if bit == section.expected_bit:
                    self.db.set_traduction(section.position, traduction)
                    if self.params.verbose:
                        print('')
                    break

        # Create the output file.
        with open(output_path, 'w') as f:
            for section in self.db.get_sections():
                f.write((section.traduction if section.traduction is not None else '-') + '\n\n')

        self.db.destroy()
