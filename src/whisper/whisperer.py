import json
from typing import Generator, Optional, cast
from pathlib import Path
from collections import Counter
from .prompt_builder import PromptBuilder
from .config import Config
from .context import Context
from .types import Vector, Bit, MessageType, Role, VerseType, Status
from .chat_gpt import ChatGPT
from .stegano_db import SteganoDb, Verse
from .conversion import Conversion
from .disk_list import DiskList
from .text_file_tool import read_sentences_from_file
from .combination import find_position
from whisper.types import Bit, Int16
import whisper.message
from dataclasses import dataclass
import whisper.combination

@dataclass
class Params:
    model: Optional[str] = None
    token: Optional[str] = None
    debug_path: Optional[str] = None
    messages_per_request: int = 6
    verbose: bool = False


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

    def __init__(self, message_type: MessageType, content: str, bit: Optional[Bit]=None, required: Optional[list[str]]=None, excluded: Optional[list[str]]=None) -> None:
        self.type: MessageType = message_type
        self.bit: Optional[Bit] = bit
        self.content: str = content
        self.required: Optional[list[str]] = required
        self.excluded: Optional[list[str]] = excluded
        if message_type == MessageType.SYSTEM:
            self.role: Role = Role.SYSTEM
        elif message_type == MessageType.USER_INIT or message_type == MessageType.USER_TERMINAL:
            if required is not None or excluded is not None or bit is not None:
                raise ValueError("required, excluded and bit are not allowed for USER_INIT and USER_TERMINAL messages.")
            self.role: Role = Role.USER
        elif message_type == MessageType.USER:
            if required is None or excluded is None or bit is None:
                raise ValueError("required, excluded and bit are required for USER messages -- required:{} excluded:{} bit:{}.".format(required, excluded, bit))
            self.role: Role = Role.USER
        else:
            self.role: Role = Role.ASSISTANT

    def to_dict(self) -> dict[str, str]:
        return {'role': self.role.value, 'content': self.content}

class Request:

    def __init__(self, messages: list[Message]) -> None:
        self.messages: list[Message] = messages

    def set_start(self, start: str) -> None:
        """Adds the start of the conversation to the first USER_INIT message."""
        start: list[str] = start.split('\n')
        for i in range(len(start)):
            if start[i] == '':
                continue
            start[i] = '{}. {}'.format(i + 1, start[i])
        for i in range(len(self.messages)):
            message: Message = self.messages[i]
            if message.type == MessageType.USER_INIT:
                text: str = '\n'.join(start)
                prompt_builder: PromptBuilder = PromptBuilder(message.content)
                message.content = prompt_builder.generate_prompt({'START': text})
                self.messages[i] = message

    def get_user_message(self, index: int) -> Message:
        """Returns the nth USER message in the request.
        The index starts at 0.

        Please note that:
        - The first message is the one whose role is SYSTEM.
        - The second message is the one whose role is USER_INIT.
        - The last message is the one whose role is USER_TERMINAL.

        The request does not contain any ASSISTANT message.
        """
        return self.messages[index+2]

    def get_user_messages_count(self) -> int:
        return len(self.messages) - 3

    def to_dict(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for message in self.messages:
            result.append(message.to_dict())
        return result

    def __len__(self) -> int:
        """Returns the number of USER messages in the request.

        Please note that:
        - The first message is the one whose role is SYSTEM.
        - The second message is the one whose role is USER_INIT.
        - The second message is the one whose role is USER_TERMINAL.

        The request does not contain any ASSISTANT message.
        """
        return len(self.messages) - 3

    def __getitem__(self, index: int) -> Message:
        return self.get_user_message(index)

    def get_message_type(self, index: int) -> MessageType:
        m: Message = self.messages[index]
        return m.type


class Whisperer:

    def __init__(self, config: Config, params: Params, db_path: Optional[str]=None) -> None:
        """Initializes the Whisperer.
        The parameters are;
          - model: the model to use for the LLM. Set to None for testing using the dry-run mode.
          - token: the token to use for the LLM. Set to None for testing using the dry-run mode.
          - debug_path: the path to the directory where the debug files will be stored.
          - messages_per_request: the number of messages per request.

        Note: the parameter "debug_path" is only used for DEBUG purposes.
        """
        # Sanity checks.
        self.chat_gpt: Optional[ChatGPT]
        if params.model is not None and params.token is not None:
            self.chat_gpt = ChatGPT(params.model, params.token)
        elif params.model is None and params.token is None:
            self.chat_gpt = None
        else:
            raise ValueError("Parameters model and token must be both set or both unset.")

        self.config: Config = config
        self.context: Context = Context(config)
        self.context.shuffle()
        self.debug_path: Optional[Path] = Path(params.debug_path) if params.debug_path is not None else None
        self.params: Params = params
        self.call_count: int = 0
        self.db_dump_count: int = 0
        if self.debug_path is not None:
            debug_path: Path = self.debug_path.joinpath('combinations.txt')
            with open(debug_path, 'w') as f:
                for i in range(len(self.context.combinations)):
                    print("%-5d: %s" % (i, json.dumps(self.context.combinations[i])), file=f)

        # Create or open the database.
        if db_path is None:
            stegano_db_path: Optional[Path] = None
            if self.debug_path is not None:
                stegano_db_path = self.debug_path.joinpath('stegano-db.sqlite')
            self.db: SteganoDb = SteganoDb(stegano_db_path.__str__() if stegano_db_path is not None else None)
        else:
            self.db: SteganoDb = SteganoDb(db_path, init=False)

    def generate_single_messages_request(self, verse: Verse) -> Request:
        messages: list[Message] = [
            Message(message_type=MessageType.SYSTEM, content=self.config.request['system']),
        ]

        if self.config.request['first_user'] is not None:
            messages.append(Message(message_type=MessageType.USER_INIT, content=self.config.request['first_user']))

        prompt_builder: PromptBuilder = PromptBuilder(self.config.request['user'])
        included = verse.combination
        prompt: str = prompt_builder.generate_prompt({'MANDATORY': json.dumps(included)})
        messages.append(Message(message_type=MessageType.USER, content=prompt, bit=verse.bit, required=included, excluded=verse.exclusions))

        if self.config.request['last_user'] is not None:
            messages.append(Message(message_type=MessageType.USER_TERMINAL, content=self.config.request['last_user']))
        return Request(messages)

    def generate_multi_messages_request(self, vector: Vector) -> Request:
        messages: list[Message] = [
            Message(message_type=MessageType.SYSTEM, content=self.config.request['system']),
        ]
        prompt_builder: PromptBuilder = PromptBuilder(self.config.request['user'])

        if self.config.request['first_user'] is not None:
            messages.append(Message(message_type=MessageType.USER_INIT, content=self.config.request['first_user']))

        for i in range(len(vector)):
            bit: Bit = vector[i]
            included, excluded = self.context.get_next_combination(bit, quoted=False)
            prompt: str = prompt_builder.generate_prompt({'MANDATORY': json.dumps(included)})
            messages.append(Message(message_type=MessageType.USER, content=prompt, bit=bit, required=included, excluded=excluded))
            if self.debug_path is not None:
                with open(self.debug_path.joinpath('generate-request.txt'), 'a') as f:
                    print("bit: {} - {}".format(bit, json.dumps(included)), file=f)

        if self.config.request['last_user'] is not None:
            messages.append(Message(message_type=MessageType.USER_TERMINAL, content=self.config.request['last_user']))
        return Request(messages)

    def generate_requests(self, vector: Vector, messages_per_request: int) -> Generator[Request, None, None]:
        full_batches_count: int = len(vector) // messages_per_request
        reminder: int = len(vector) % messages_per_request
        if self.params.verbose:
            print('Number of full batches:      {} ({} messages each)'.format(full_batches_count, messages_per_request))
            print('Number of reminder messages: {}'.format(reminder))
        for i in range(full_batches_count):
            request: Request = self.generate_multi_messages_request(vector[i * messages_per_request:(i + 1) * messages_per_request])
            yield request
        if reminder > 0:
            request: Request = self.generate_multi_messages_request(vector[full_batches_count * messages_per_request:])
            yield request

    def save_request_for_debug(self, request: Request, call_count: int) -> None:
        if self.debug_path is None:
            return
        debug_path: Path = self.debug_path.joinpath('request-{}.json'.format(call_count))
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

    def save_db_for_debug(self):
        if self.debug_path is None:
            return
        p: Path = self.debug_path.joinpath('stegano-db-dump-{}.txt'.format(self.db_dump_count))
        self.db_dump_count += 1
        self.db.dump(p.__str__())

    def check_verses(self) -> int:
        count: int = 0
        for verse in self.db.get_verses():
            if verse.verse_type != VerseType.HIDE or verse.status == Status.SUCCESS:
                continue

            expected: list[str] = Conversion.unquote_list(verse.combination)
            if self.params.verbose:
                print('Checking verse #{} [{}/{}]: {}'.format(verse.position,
                                                              verse.status,
                                                              verse.verse_type,
                                                              verse.verse))
                print("Expecting: {}".format(expected))
            found: list[list[str]] = whisper.combination.search(verse.verse, self.context.combinations)

            # We should found exactly one combination: the one used to generate the verse.
            if len(found) != 1:
                if self.params.verbose:
                    print('INVALID: Found {} combinations instead of 1 -- {}'.format(len(found), found))
                count += 1
                self.db.set_status(verse.position, Status.ERROR)
                continue
            if Counter(found[0]) != Counter(expected):
                if self.params.verbose:
                    print('INVALID: expected {} but found {}'.format(expected, found[0]))
                count += 1
                self.db.set_status(verse.position, Status.ERROR)
                continue
            if self.params.verbose:
                print('VALID')
            self.db.set_status(verse.position, Status.SUCCESS)
        return count

    def exec_request(self, request: Request) -> list[str]:
        self.save_request_for_debug(request, self.call_count)
        d: list[dict[str, str]] = request.to_dict()
        try:
            response: str = self.chat_gpt.call(d)
        except Exception as e:
            raise RuntimeError("Error calling the LLM: {}".format(str(e)))
        self.save_response_for_debug(response, self.call_count)
        verses: list[str] = json.loads(response)['results']
        self.call_count += 1
        return verses

    def hide(self, input_path: str, output_path: str) -> None:
        context: Context = Context(self.config)
        context.shuffle()
        start: str = self.config.first_lines

        # Load the input file.
        v: Vector = whisper.message.Message.load_text_file_as_vector(input_path, length=16)

        # Generate the requests, execute them, and save the results into the database.
        position: int = 0
        for request in self.generate_requests(v, self.params.messages_per_request):
            # Execute the request.
            request.set_start(start)
            new_verse: list[str] = self.exec_request(request)
            if request.get_user_messages_count() != len(new_verse):
                raise RuntimeError("The number of messages returned by the LLM does not match the number of messages in the request (expected: {}, found: {}).\n\n{}\n\n{}".format(self.params.messages_per_request, len(new_verse), json.dumps(request.to_dict(), indent=2, ensure_ascii=False), json.dumps(new_verse, indent=2, ensure_ascii=False)))

            # Save the request and the response into the database.
            if self.params.verbose:
                print('Saving the {} results into the database...'.format(len(new_verse)))
            for i in range(len(new_verse)):
                user_message: Message = request.get_user_message(i)
                self.db.add_verse(position,
                                  new_verse[i], # Verse that has been generated by the LLM.
                                  VerseType.HIDE,
                                  user_message.required,
                                  user_message.excluded,
                                  user_message.content,
                                  user_message.bit)
                if self.debug_path is not None:
                    debug_path = self.debug_path.joinpath('1-hide.txt')
                    with open(debug_path, 'a') as f:
                        print('%-4d - %s\n       %s (%d)' % (position, new_verse[i], user_message.required, user_message.bit), file=f)
                position += 1
        self.save_db_for_debug()

        # Check the generated verses and ask for correction if needed.
        error_count: int = self.check_verses()
        while error_count > 0:
            if self.params.verbose:
                print('\n{} verses are invalid...'.format(error_count))
            for verse in self.db.get_invalid_verses():
                request = self.generate_single_messages_request(verse)
                user_message: Message = request.get_user_message(0)
                new_verse = self.exec_request(request)

                if 1 != len(new_verse):
                    raise RuntimeError("The number of messages returned by the LLM does not match the number of messages in the request (expected: 1, found: {}).\n\n{}\n\n{}".format(len(new_verse), json.dumps(request.to_dict(), indent=2, ensure_ascii=False), json.dumps(new_verse, indent=2, ensure_ascii=False)))

                if self.debug_path is not None:
                        with open(self.debug_path.joinpath('generate-request.txt'), 'a') as f:
                            print('Ask the LLM to reformulate the verse #{}:'.format(verse.position), file=f)
                            print("   - {}".format(verse.verse), file=f)
                            print("   - {}".format(verse.prompt.strip()), file=f)
                            print("   - {}".format(new_verse), file=f)

                self.db.set_verse(verse.position,
                                  new_verse[0],
                                  Conversion.unquote_list(user_message.required),
                                  Conversion.unquote_list(user_message.excluded),
                                  user_message.content)
            self.save_db_for_debug()
            error_count = self.check_verses()
        self.save_db_for_debug()

        # Generate the output.
        with open(output_path, 'w') as f:
            for verse in self.db.get_verses():
                if verse.verse_type == VerseType.HIDE:
                    f.write(verse.verse + '\n')

class Revealer:

    def __init__(self, config: Config, murmur: str, reveal_path: str, verbose: bool = False, debug_path: Optional[str] = None) -> None:
        self.config: Config = config
        self.context: Context = Context(config)
        self.context.shuffle()
        self.murmur: str = murmur
        self.reveal_path: str = reveal_path
        self.verbose: bool = verbose
        self.expected_combinations: list[list[str]] = []
        self.debug_path: Optional[Path] = Path(debug_path) if debug_path is not None else None
        for l in self.context.combinations:
            self.expected_combinations.append(Conversion.unquote_list(l))
        if self.debug_path is not None:
            debug_path = self.debug_path.joinpath('reveal-combinations.txt')
            with open(debug_path, 'w') as f:
                for i in range(len(self.context.combinations)):
                    print("%-5d: %s" % (i, json.dumps(self.context.combinations[i])), file=f)

    @staticmethod
    def load_text_file_as_sentences(path: str) -> DiskList:
        sentences: DiskList = DiskList()
        for sentence in read_sentences_from_file(path):
            sentences.append(sentence)
        return sentences

    def find_parity(self, sentence: str) -> Bit:
        found: list[list[str]] = whisper.combination.search(sentence, self.expected_combinations)
        if len(found) != 1:
            raise ValueError("{}\nExpected exactly one combination, found {} instead ({}).".format(sentence, len(found), found))
        if self.debug_path is not None:
            debug_path = self.debug_path.joinpath('reveal-process-input.txt')
            with open(debug_path, 'a') as f:
                print("       %s" % (found[0]), file=f)
        position = find_position(self.expected_combinations, found[0])
        return cast(Bit, position % 2)

    def reveal(self) -> None:
        # Load the murmur into a series of lines
        murmur_db: DiskList = Revealer.load_text_file_as_sentences(self.murmur)
        if self.debug_path is not None:
            debug_path = self.debug_path.joinpath('reveal-process-input.txt')
            if debug_path.exists():
                debug_path.unlink()
        try:
            # Create a vector of bits.
            bits: list[Bit] = []
            line_num: int = 0
            error_count: int = 0
            for line in murmur_db:
                try:
                    if self.debug_path is not None:
                        debug_path = self.debug_path.joinpath('reveal-process-input.txt')
                        with open(debug_path, 'a') as f:
                            print("%-5d: %s" % (line_num, line), file=f)
                    parity: Bit = self.find_parity(line)
                    bits.append(parity)

                    if self.debug_path is not None:
                        debug_path = self.debug_path.joinpath('reveal-process-input.txt')
                        with open(debug_path, 'a') as f:
                            print("       %s" % ("even (0)" if parity == 0 else "odd (1)"), file=f)

                except ValueError as e:
                    print("Error processing line {}: {}".format(line_num, str(e)))
                    error_count += 1
                line_num += 1

            if error_count > 0:
                print("Found {} errors in the murmur. Please check the file {}.".format(error_count, self.murmur))
                exit(1)

            # Make sure that the number of bits is greater than 64.
            if len(bits) < 16:
                raise ValueError("The murmur must contain at least 16 sentences!")
            length_vector: list[Bit] = bits[:16]


            if self.debug_path is not None:
                debug_path = self.debug_path.joinpath('reveal-process-input.txt')
                with open(debug_path, 'a') as f:
                    print("\n\n\n", file=f)
                    print("%s" % (length_vector), file=f)


            length: Int16 = Conversion.bit_list_to_int16(length_vector)
            body_vector: list[Bit] = bits[16:16+length*8]
            body = Conversion.bit_list_to_bytes(body_vector)
            if self.verbose:
                print("Data: {}".format(bits))
                print("length vector: {}".format(length_vector))
                print("length: {} (characters) => {} bits".format(length, length*8))
                print("body: {}".format(body_vector))
                print('Message: "{}"'.format(self.reveal_path))
            with open(self.reveal_path, 'w') as f:
                f.write(str(body, 'ascii'))
        finally:
            murmur_db.destroy()

