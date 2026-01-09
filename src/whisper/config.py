from typing import Optional
from dataclasses import dataclass
import yaml

@dataclass
class Config:
    model: str
    temperature: float
    top_p: float
    system: dict[str, str]
    assistant: Optional[str]
    user: str

def load_config(file_path: str) -> Config:
    """
    Loads configuration from a YAML file and validates required fields.

    This function reads the specified YAML file, ensures it parses into a
    dictionary.

    :param file_path: The path to the YAML configuration file.
    :return: A Config object populated with data from the file.
    :raises ValueError: If the file content is not a dictionary or if required keys are missing.
    """
    conf: dict
    with open(file_path) as stream:
        conf = yaml.safe_load(stream)

    # Check first level keys
    if not isinstance(conf, dict):
        raise ValueError("Config file must represent a dictionary.")
    if ('model' not in conf or
            'temperature' not in conf or
            'top_p' not in conf or
            'system' not in conf or
            'assistant' not in conf or
            'user' not in conf):
        raise ValueError("Config file must contain 'model', 'temperature', 'top_p', 'system', 'assistant' and 'user' keys.")

    if not isinstance(conf['model'], str):
        raise ValueError("'model' must be a string.")
    if not isinstance(conf['temperature'], float):
        raise ValueError("'temperature' must be a float.")
    if not isinstance(conf['top_p'], float):
        raise ValueError("'top_p' must be a float.")
    if not isinstance(conf['system'], dict):
        raise ValueError("'system' must be a dictionary.")
    if not (isinstance(conf['assistant'], str) or conf['assistant'] is None):
        raise ValueError("'assistant' must be a string or null.")
    if not isinstance(conf['user'], str):
        raise ValueError("'user' must be a string (got '{}' instead).".format(conf['user']))

    # Check second level keys
    expected_keys: list[str] = ['first_request', 'next_requests']
    for key in expected_keys:
        if key not in conf['system']:
            raise ValueError("'system' must contain '{}' key.".format(key))
        if not isinstance(conf['system'][key], str):
            raise ValueError("'system.{}' must be a string.".format(key))
        conf['system'][key] = conf['system'][key].strip()

    for key in ['model', 'assistant', 'user']:
        if isinstance(conf[key], str):
            conf[key] = conf[key].strip()

    # Create the config object and return it
    return Config(conf["model"], conf["temperature"], conf["top_p"], conf["system"], conf["assistant"], conf["user"])
