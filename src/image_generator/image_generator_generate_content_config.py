class ImageGeneratorGenerateContentConfig:

    def __init__(self):
        self.prompt = ""
        self.optional_config = {}

    def set_prompt(self, prompt: str):
        self.prompt = prompt

    def set_temperature(self, temperature: float) -> None:
        self.optional_config['temperature'] = temperature

    def set_top_p(self, top_p: float) -> None:
        self.optional_config['top_p'] = top_p

    def get_prompt(self) -> str:
        return self.prompt

    def get_temperature(self) -> float | None:
        return self.optional_config.get('temperature')

    def get_top_p(self) -> float | None:
        return self.optional_config.get('top_p')
