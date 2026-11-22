"""Delegate Greek/English translation, then check protected placeholders and glossary terms."""

import re
from collections import Counter
from typing import Literal

from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

ENGLISH = "Hello {name}. Your order {order_id} is ready."
GREEK = "Γεια σου {name}. Η παραγγελία σου {order_id} είναι έτοιμη."
DEFAULT = {"text": ENGLISH, "target": "el", "glossary": {"order": "παραγγελία"}}


class Input(Record):
    text: str
    target: Literal["el", "en"]
    glossary: dict[str, str]


class Translation(Record):
    target: Literal["el", "en"]
    text: str


def verify(answer: Translation, data: Input) -> None:
    require(
        answer.target == data.target and bool(answer.text.strip()), "translation target mismatch"
    )

    def placeholders(text):
        return Counter(re.findall(r"\{[A-Za-z_][A-Za-z_0-9]*\}", text))

    require(placeholders(answer.text) == placeholders(data.text), "protected placeholder mismatch")
    for source, target in data.glossary.items():
        if source.casefold() in data.text.casefold():
            require(
                target.casefold() in answer.text.casefold(), "required glossary term is missing"
            )


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    fixtures = {(ENGLISH, "el"): GREEK, (GREEK, "en"): ENGLISH}
    if ctx.provider == "offline" and (data.text, data.target) not in fixtures:
        raise ValueError(
            "offline translation replays the English/Greek pair; use a provider for other text"
        )
    golden = Translation(target=data.target, text=fixtures.get((data.text, data.target), ""))
    translator = ctx.agent(
        "translator",
        [encoded(golden)],
        output_type=Translation,
        instructions="Translate into the requested language. Preserve every {placeholder} "
        "verbatim, including repetitions, and apply the supplied glossary.",
    )
    prompt = encoded(data)
    coordinator = ctx.agent(
        "localization_editor",
        [call("translate", task=prompt), encoded(golden)],
        tools=[translator.as_tool(name="translate", read_only=True)],
        output_type=Translation,
        instructions="Delegate to translate. Return its target and translated text.",
    )
    answer = await ctx.execute(coordinator, prompt)
    verify(answer, data)
    ctx.artifact("translation.json", answer)
    return {
        **answer.model_dump(),
        "checks": "placeholders and glossary; semantic quality needs review",
    }
