"""Optional surrounding context supplied with a source or candidate text."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from semantica.core.document import Document
from semantica.errors import InputError


@dataclass(frozen=True)
class Context:
    """Preceding text that may resolve pronouns or other context-dependent expressions.

    The toolkit does not resolve coreference. Context is used only to decide whether a
    context-dependent difference can be *reviewed* rather than merely *flagged as unverifiable*.
    """

    sentences: tuple[str, ...] = ()

    @classmethod
    def from_texts(cls, texts: Iterable[str] | None) -> Context:
        if texts is None:
            return cls()
        items: list[str] = []
        for text in texts:
            if not isinstance(text, str):
                raise InputError("context entries must be strings")
            if text.strip():
                items.extend(s.text for s in Document.from_text(text).sentences)
        return cls(tuple(items))

    @property
    def is_empty(self) -> bool:
        return not self.sentences
