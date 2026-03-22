from pathlib import Path

import main


def load_prompt(name: str) -> str:
    prompt_path = main.get_project_path() / 'prompts' / f'{name}.prompt'
    return prompt_path.read_text(encoding='utf-8')

