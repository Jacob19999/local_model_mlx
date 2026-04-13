from __future__ import annotations

from local_model.services.reasoning_parser import ReasoningParser


def test_reasoning_parser_handles_partial_open_and_close_tags() -> None:
    parser = ReasoningParser("think_tags")

    answer_delta, reasoning_delta = parser.feed("<thi")
    assert answer_delta == ""
    assert reasoning_delta == ""

    answer_delta, reasoning_delta = parser.feed("nk>step")
    assert answer_delta == ""
    assert reasoning_delta == "step"

    answer_delta, reasoning_delta = parser.feed(" one</th")
    assert answer_delta == ""
    assert reasoning_delta == " one"

    answer_delta, reasoning_delta = parser.feed("ink>Answer")
    assert answer_delta == "Answer"
    assert reasoning_delta == ""


def test_reasoning_parser_normalizes_closing_tag_without_explicit_open_tag() -> None:
    parser = ReasoningParser("think_tags")

    answer_delta, reasoning_delta = parser.feed("scratch work</think>Final answer")

    assert answer_delta == "Final answer"
    assert reasoning_delta == "scratch work"


def test_reasoning_parser_passes_through_non_reasoning_text() -> None:
    parser = ReasoningParser("none")

    answer_delta, reasoning_delta = parser.feed("Plain answer")

    assert answer_delta == "Plain answer"
    assert reasoning_delta == ""
