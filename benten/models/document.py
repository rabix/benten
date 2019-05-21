import pathlib

from .createmodel import create_model, Base, Undefined

import logging
logger = logging.getLogger(__name__)


class Document:

    def __init__(self,
                 doc_uri: str,
                 text: str,
                 version: int,
                 language_models: dict):
        self.doc_uri = doc_uri
        self.text = text
        self.version = version
        self.language_models = language_models

        self.use_last_good_model = True

        self._current_parsed_model: Base = None
        self._last_good_model: Base = None

        self.update(text)

    @property
    def model(self) -> Base:
        return self._last_good_model if self.use_last_good_model else self._current_parsed_model

    def update(self, new_text):
        self.text = new_text
        self._current_parsed_model = create_model(self.doc_uri, self.text, self.language_models)

        if self._last_good_model is None or not isinstance(self._current_parsed_model, Undefined):
            self._last_good_model = self._current_parsed_model

        if self._current_parsed_model.problems:
            self._last_good_model.problems += self._current_parsed_model.problems
            self._last_good_model.problems = list(set(self._last_good_model.problems))
