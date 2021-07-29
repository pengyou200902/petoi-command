from typing import Text, List

import logging

LOG_FORMAT = '%(asctime)-15s %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class Command:
    """
    ~~~language: The language of the text. eg: "en" means English, "zh" means Chinese.~~~

    text: This is the result text of the Speech Recognizer, such as "sit down" or "stand up".

    command: The Petoi command that maps to the text. eg: text="sit down", command="ksit".

    description: The introduction of this command/object.
    """
    def __init__(self, text, command, description):
        # self.language = language
        self.text = text
        self.command = command
        self.description = description

    # @property
    # def language(self) -> Text:
    #     return self._language
    #
    # @language.setter
    # def language(self, val: Text):
    #     if val:
    #         self._language = val
    #     else:
    #         msg = "The language of the text should be specified."
    #         logger.error(msg)
    #         raise ValueError(msg)

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, val: Text):
        if val:
            self._text = val
        else:
            msg = "A command should have a text."
            logger.error(msg)
            raise ValueError(msg)

    @property
    def command(self) -> Text:
        return self._command

    @command.setter
    def command(self, val: Text):
        if val:
            self._command = val
        else:
            msg = "A Command object should be mapped to a Petoi command."
            logger.error(msg)
            raise ValueError(msg)

    @property
    def description(self) -> Text:
        return self._description

    @description.setter
    def description(self, val: Text):
        if val:
            self._description = val
        msg = "A Command object should have a description."
        logger.error(msg)
        raise ValueError(msg)

    def __repr__(self):
        return {'text': self.text, 'command': self.command}

