from pathlib import Path

_project_path = Path(__file__).parent

def get_project_path() ->  Path:
    return _project_path


