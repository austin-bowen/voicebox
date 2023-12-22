__all__ = ['SSML']

from typing import Union


class SSML(str):
    """
    A `Speech Synthesis Markup Language (SSML)
    <https://www.w3.org/TR/speech-synthesis/>`_ string.

    By wrapping a string in this class, the string is treated as SSML
    by :class:`TTS` engines that support it.

    Example:
        >>> from voicebox.tts import ESpeakNG
        >>> from voicebox import SSML
        >>> tts = ESpeakNG()
        >>> text = SSML('<speak>Hello world</speak>')
        >>> audio = tts.get_speech(text)
    """

    @classmethod
    def auto(cls, text: str) -> Union['SSML', str]:
        """
        Returns the ``text`` as SSML if it starts with ``'<speak>'``,
        otherwise returns the ``text`` unaltered.

        Example:
            >>> from voicebox import SSML
            >>> SSML.auto('<speak>Hello world</speak>')
            SSML('<speak>Hello world</speak>')
            >>> SSML.auto('Hello world')
            'Hello world'
        """

        is_ssml = text.lstrip().startswith('<speak>')
        return cls(text) if is_ssml else text
