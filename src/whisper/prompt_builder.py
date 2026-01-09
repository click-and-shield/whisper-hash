from pprint import pprint


class PromptBuilder:

    def __init__(self, template: str) -> None:
        self.template: str = template

    def generate_prompt(self, variables: dict[str, str]) -> str:
        try:
            return self.template.format(**variables)
        except KeyError as e:
            print("Error formatting prompt:\n\ntemplate:\n\n{}\n\nvariables:\n\n{}\n\nmessage:\n\n{}\n\n".format(self.template, variables, e))
            raise e

    