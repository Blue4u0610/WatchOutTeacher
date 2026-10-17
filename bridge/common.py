import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('COURSE_ASSIST_DATA', str(Path.home() / 'Library/Application Support/CourseAssist')))
MAX_FILE = 30 * 1024 * 1024

class AppError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code, self.message = code, message

def require(value, message):
    if not value:
        raise AppError('invalid_input', message)

def short_text(value, limit, label):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit, f'{label}为空或超过 {limit} 字符。')
    return value.strip()
