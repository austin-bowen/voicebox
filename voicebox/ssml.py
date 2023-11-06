"""Module for constructing SSML strings."""

from typing import List, Union, Dict


class SSML(str):
    """A [Speech Synthesis Markup Language (SSML)](https://www.w3.org/TR/speech-synthesis/) string."""

    @classmethod
    def auto(cls, text: str) -> Union['SSML', str]:
        """
        Returns the ``text`` as SSML if it starts with ``'<speak>'``,
        otherwise returns the ``text`` unaltered.
        """

        is_ssml = text.lstrip().startswith('<speak>')
        return cls(text) if is_ssml else text


class _SSMLElement:
    tag: str
    attributes: Dict[str, str]
    elements: List[Union[str, '_SSMLElement']]

    def __init__(self, tag: str, **attributes: str):
        self.tag = tag
        self.attributes = attributes
        self.elements = []

    @property
    def content(self) -> str:
        return ' '.join(map(str, self.elements))

    def __str__(self) -> SSML:
        attributes = ' '.join(
            f'{key}="{value}"'
            for key, value in self.attributes.items()
        )

        content = self.content

        return SSML(''.join([
            f'<{self.tag}',
            f' {attributes}' if attributes else '',
            f'>{content}</{self.tag}>' if content else '/>',
        ]))

    def add(self, element: Union[str, '_SSMLElement']) -> '_SSMLElement':
        self.elements.append(element)
        return self

    def say(self, text: str) -> '_SSMLElement':
        return self.add(text)

    def break_(self, seconds: Union[int, float]) -> '_SSMLElement':
        if isinstance(seconds, float):
            time = round(seconds * 1000)
            time = f'{time}ms'
        else:
            time = f'{seconds}s'

        return self.add(_SSMLElement('break', time=time))

    def say_as(self, text: str, interpret_as: str, format: str = None, detail: str = None) -> '_SSMLElement':
        attributes = {'interpret-as': interpret_as}
        if format is not None:
            attributes['format'] = format
        if detail is not None:
            attributes['detail'] = detail

        return self.add(_SSMLElement('say-as', **attributes).add(text))

    def audio(self, src: str) -> '_SSMLElement':
        # TODO Implement other attributes
        return self.add(f'<audio src="{src}"/>')

    def paragraph(self, *sentences: Union[str, '_SSMLElement']) -> '_SSMLElement':
        p = Paragraph()
        for sentence in sentences:
            p.sentence(sentence)

        return self.add(p)

    def sub(self, alias: str, text: str) -> '_SSMLElement':
        return self.add(_SSMLElement('sub', alias=alias).add(text))


class SSMLBuilder(_SSMLElement):
    def __init__(self):
        super().__init__('speak')

    def build(self) -> SSML:
        return SSML(self)


class Paragraph(_SSMLElement):
    def __init__(self):
        super().__init__('p')

    def sentence(self, text: str) -> 'Paragraph':
        return self.add(Sentence(text))


class Sentence(_SSMLElement):
    def __init__(self, text: str = None):
        super().__init__('s')

        if text is not None:
            self.say(text)


def main():
    ssml = (
        SSMLBuilder()
        .say('Hello, world!')
        .break_(12.3456)
        .say('This is a test.')
        .say_as('1234', 'cardinal', format='digits', detail='1')
        .paragraph('This is a sentence.', 'This is another sentence.')
        .sub('alias', 'text')
        .build()
    )

    print(ssml)


if __name__ == '__main__':
    main()
