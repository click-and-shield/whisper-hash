from pprint import pprint


class PromptBuilder:

    def __init__(self, template: str) -> None:
        self.template: str = template

    def generate_prompt(self, variables: dict[str, str]) -> str:
        return self.template.format(**variables)

    