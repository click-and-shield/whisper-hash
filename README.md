# Whisper hash

## Introduction

This project explores the sophisticated intersection of Large Language Models (LLMs) and steganography.
It implements a keyed steganographic approach, where a secret message is embedded within a "haystack" of generated text, recoverable only by those in possession of a specific secret key.

While earlier iterations—such as *whisper-parity* and *whisper-verse*—produced outputs that were relatively easy to identify as steganographic carriers, this project focuses on high-fidelity stealth.
By generating text that closely mimics natural linguistic patterns, it ensures that hidden messages remain remarkably difficult to detect, making systematic analysis prohibitively resource-intensive.

Key Terminology:
- **Needle**: The secret message intended for concealment.
- **Haystack**: The final generated text containing the hidden information.
- **Cover Message**: The original text body used as a template or source to generate the haystack.

## How it works

### Overview

### Overview

The algorithm operates using the following components:

*   **Hashing Suite**: A predefined sequence of hashing functions (including `md5`, `sha256`, `sha512`, and the `sha3` family). For a complete list, see [hasher.py](src/whisper/hasher.py).
*   **Secret Key**: A user-provided passphrase.
*   **Cover Message**: A base text provided by the user. Our example uses an [AI-generated analysis of George Orwell's *1984*](test-data/cover-message.txt).
*   **Hidden Message**: The target data to be concealed (the "needle").

The steganographic process follows these steps:

1.  **Binary Encoding**: The "needle" is converted into a raw bitstream.
2.  **Key Derivation**: A 32-byte master key (*k*) is derived from the secret key using the Argon2id algorithm.
3.  **Haystack Construction**:
    For each bit (*b*) at position (*p*) in the bitstream (the bitstream being the binary representation of the "needle"):
    1.  The *p*-th paragraph (*P*) of the cover message is selected.
    2.  A specific hash function (*H*) is chosen from the suite based on the current state of the key (*k*) and the position (*p*).
    3.  The paragraph is hashed: $R = H(P)$.
    4.  To increase computational complexity and security, the result is processed again: $S = Argon2id(R)$.
    5.  A parity bit (*B*) is calculated by summing the bytes of $R$ modulo 2 ($B = \sum R \pmod 2$).
    6.  **Bit Matching**:
        *   If $B$ matches the target bit $b$, the paragraph $P$ is accepted into the final haystack.
        *   If $B$ does not match, a Large Language Model (LLM) reformulates the paragraph $P$, and the process repeats from step 3.3 until the parity matches.

> **Note on Key Evolution**: The derived key *k* is dynamic. Once the position *p* exceeds the key length (32 bytes), *k* is updated by XOR-combining its current value with the most recent hash *S*.
>
> For technical implementation details, please consult [hasher.py](src/whisper/hasher.py).

### Detailed description

#### Presentation

Let's take an example:

* *needle*: "Hello World!"
* *secret key*: "secret-key"
* *cover message*s: see [cover-message.txt](test-data/cover-message.txt)

#### Conversion of the needle into a binary representation

First, we convert the needle is converted into a binary representation:

The 16 first bits of the binary representation represent the length, in bytes, of the needle.

```
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0
```

The length of the needle is: `2^0*0 + 2^1*0 + 2^2*1 + 2^3*1 = 12 bytes`.

> Indeed, the string of characters "Hello World!" is 12 bytes long.

Then, the remaining (`12*8 = 96`) bits of the binary representation represent the needle itself.

| *byte*  | *binary representation*  | *char* |
|---------|--------------------------|--------|    
| byte 2  | [0, 1, 0, 0, 1, 0, 0, 0] | '`H`'  |
| byte 3  | [0, 1, 1, 0, 0, 1, 0, 1] | '`e`'  |
| byte 4  | [0, 1, 1, 0, 1, 1, 0, 0] | '`l`'  |
| byte 5  | [0, 1, 1, 0, 1, 1, 0, 0] | '`l`'  |
| byte 6  | [0, 1, 1, 0, 1, 1, 1, 1] | '`o`'  |
| byte 7  | [0, 0, 1, 0, 0, 0, 0, 0] | '` `'  |
| byte 8  | [0, 1, 0, 1, 0, 1, 1, 1] | '`W`'  |
| byte 9  | [0, 1, 1, 0, 1, 1, 1, 1] | '`o`'  |
| byte 10 | [0, 1, 1, 1, 0, 0, 1, 0] | '`r`'  |
| byte 11 | [0, 1, 1, 0, 1, 1, 0, 0] | '`l`'  |
| byte 12 | [0, 1, 1, 0, 0, 1, 0, 0] | '`d`'  |
| byte 13 | [0, 0, 1, 0, 0, 0, 0, 1] | '`!`'  |

#### Key derivation

The secret key is hashed using Argon2 to generate a 32-byte hash value:

Code:

```python
        from argon2.low_level import hash_secret_raw, Type
        KEY_LENGTH: int = 32
        
        key: bytes = hash_secret_raw(
            secret=secret_key.encode(),
            salt=bytes(1024),
            time_cost=3,
            memory_cost=65536,
            parallelism=1,
            hash_len=KEY_LENGTH,
            type=Type.ID
        )
```

> See [code](src/whisper/hasher.py) for more details.

Result (for the secret key "secret-key"): `7db00b8e2ee8259f55c08aed633659ab0f8a555de3ae9f6e0bc69d0f18fdecec`

The list of hashing functions contains 11 elements (See variable `ALGORITHMS` [here](src/whisper/hasher.py)).

```python
ALGORITHMS: list[str] = ['md5', 'sha224', 'sha256', 'sha384', 'sha512', 'sha512_224', 'sha512_256', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512']
```

| *index* | *byte* | *position in list of hash function* | *hash function* |
|---------|--------|-------------------------------------|-----------------|
| 0       | 125    | 4 (125 % 11)                        | sha512          |
| 1       | 176    | 0 (176 % 11)                        | md5             |
| 2       | 11     | 0 (11 % 11)                         | md5             |
| 3       | 142    | 10                                  | sha3_512        |
| 4       | 46     | 2                                   | sha256          |
| 5       | 232    | 1                                   | sha224          |
| 6       | 37     | 4                                   | sha512          |
| 7       | 159    | 5                                   | sha512_224      |
| 8       | 85     | 8                                   | sha3_256        |
| 9       | 192    | 5                                   | sha512_224      |
| 10      | 138    | 6                                   | sha512_256      |
| 11      | 237    | 6                                   | sha512_256      |
| 12      | 99     | 0                                   | md5             |
| 13      | 54     | 10                                  | sha3_512        |
| 14      | 89     | 1                                   | sha224          |
| 15      | 171    | 6                                   | sha512_256      |
| 16      | 15     | 4                                   | sha512          |
| 17      | 138    | 6                                   | sha512_256      |
| 18      | 85     | 8                                   | sha3_256        |
| 19      | 93     | 5                                   | sha512_224      |
| 20      | 227    | 7                                   | sha3_224        |
| 21      | 174    | 9                                   | sha3_384        |
| 22      | 159    | 5                                   | sha512_224      |
| 23      | 110    | 0                                   | md5             |
| 24      | 11     | 0                                   | md5             |
| 25      | 198    | 0                                   | md5             |
| 26      | 157    | 3                                   | sha384          |
| 27      | 15     | 4                                   | sha512          |
| 28      | 24     | 2                                   | sha256          |
| 29      | 253    | 0                                   | md5             |
| 30      | 236    | 5                                   | sha512_224      |
| 31      | 236    | 5                                   | sha512_224      |

Thus:

* The first hash function used will be `sha512`.
* The second hash function used will be `md5`.
* The third hash function used will be `md5`.
* ...
* The 32-th hash function used will be `sha512_224`.

> The 33-th hash function used is unknown at this point.
> Read the overview: _The derived key *k* is dynamic. Once the position *p* exceeds the key length (32 bytes), *k* is updated by XOR-combining its current value with the most recent hash *S*._

#### Haystack Construction

* **Hiding the first bit of the needle**  
  The first bit of the needle's binary representation is `0`.  
  The initial paragraph of our cover message is as follows:
  > Le roman *1984* commence par une atmosphère pesante et oppressante, dans laquelle chaque détail du quotidien semble chargé d’un malaise latent...

  Using `sha512` as the hash function, we determine the parity bit for this paragraph:

  ```python
  from whisper.hasher import Hasher
  
  hasher = Hasher("secret-key", verbose=True)
  b: int = hasher.get_parity("sha512", "Le roman *1984* commence...")
  ```

  In this case, the resulting value `b` is `0`. Since it matches the first bit of our needle, the paragraph is appended to the haystack in its original form.

* **Hiding the second bit of the needle**  
  The second bit of the needle's binary representation is also `0`.  
  The second paragraph of the cover message is:
  > Le lecteur découvre très vite que le temps lui-même est suspect. Les horloges qui sonnent treize heures...

  For this step, the `md5` hash function is employed. We calculate the parity bit for the paragraph:

  ```python
  b: int = hasher.get_parity("md5", "Le lecteur découvre très vite...")
  ```

  The resulting value `b` is `1`, which does not match the required needle bit (`0`). To resolve this, we utilize an LLM to reformulate the paragraph while preserving its original meaning.

  The prompt sent to the model is structured as follows:

  ```json
  [
    {
      "role": "system",
      "content": "Tu es un écrivain professionnel. Tu dois reformuler le texte ci-après, en conservant fidèlement le sens..."
    },
    {
      "role": "user",
      "content": "Le lecteur découvre très vite que le temps lui-même est suspect..."
    }
  ]
  ```

  **Resulting reformulation:**
  > Le lecteur perçoit rapidement que la notion même de temps devient douteuse. Les horloges indiquant treize heures...

  The parity bit for this new version is calculated. Since it now returns `0`, the reformulated paragraph is successfully added to the haystack.

* **Iterative Process**  
  This procedure is repeated for each subsequent bit of the needle until the entire message is hidden within the generated haystack.

## Run the example

### Requirements

You need:
- Python 3.10.12 or higher.
- A [OpenAI API key](https://platform.openai.com/account/api-keys).
- [pipenv](https://pipenv.pypa.io/en/latest/) (`pip install --user pipenv`)

### Prepare the environment

- Create a virtual environment: `python -m venv .venv`
- Activate the virtual environment:
    * linux: `source .venv/bin/activate`
    * windows: `.venv\Scripts\activate.bat`
- Install the dependencies: `pip install -e .`.
- Verify that everything is working fine: `python -m unittest discover tests/`

> *Note*:
> - Create the file "requirements.txt": `pip freeze > requirements.txt`

### Run the scripts

Hide the message:

    cd app
    python hide.py --debug --verbose --token /home/dev/.token ../test-data/config.yaml secret-key ../test-data/needle.txt ../test-data/cover-message.txt output.txt

Reveal the message:

    cd app
    python -u reveal.py --verbose secret-key ../test-data/output.txt message.txt


* needle: [message.txt](test-data/needle.txt)
* cover message: [cover-message.txt](test-data/cover-message.txt)
* haystack: [output.txt](test-data/output.txt)
* configuration: [config.yaml](test-data/config.yaml)
* debug data: [debug.tar](test-data/debug.tar)

