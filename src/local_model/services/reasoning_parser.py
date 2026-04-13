from __future__ import annotations

from local_model.models import ReasoningTranscript

OPEN_TAG = "<think>"
CLOSE_TAG = "</think>"


def _incomplete_tag_suffix(text: str, tags: tuple[str, ...]) -> str:
    max_length = min(len(text), max(len(tag) for tag in tags) - 1)
    for size in range(max_length, 0, -1):
        suffix = text[-size:]
        if any(tag.startswith(suffix) for tag in tags):
            return suffix
    return ""


class ReasoningParser:
    def __init__(self, reasoning_format: str = "none") -> None:
        self.transcript = ReasoningTranscript(format=reasoning_format)

    def feed(self, text: str) -> tuple[str, str]:
        if not text:
            return "", ""
        if self.transcript.format == "none":
            self.transcript.answer_buffer += text
            return text, ""

        self.transcript.pending_buffer += text
        return self._drain(final=False)

    def finalize(self) -> tuple[str, str]:
        if self.transcript.format == "none":
            return "", ""
        answer_delta, reasoning_delta = self._drain(final=True)
        self.transcript.pending_buffer = ""
        self.transcript.open_segment = False
        return answer_delta, reasoning_delta

    def _drain(self, *, final: bool) -> tuple[str, str]:
        answer_parts: list[str] = []
        reasoning_parts: list[str] = []
        tags = (OPEN_TAG, CLOSE_TAG)

        while self.transcript.pending_buffer:
            buffer = self.transcript.pending_buffer
            if self.transcript.open_segment:
                closing_index = buffer.find(CLOSE_TAG)
                if closing_index == -1:
                    if final:
                        reasoning_text = buffer
                        remainder = ""
                    else:
                        suffix = _incomplete_tag_suffix(buffer, (CLOSE_TAG,))
                        remainder = suffix
                        reasoning_text = buffer[: len(buffer) - len(remainder)] if remainder else buffer
                    if reasoning_text:
                        reasoning_parts.append(reasoning_text)
                        self.transcript.raw_buffer += reasoning_text
                        self.transcript.normalized_buffer += reasoning_text
                    self.transcript.pending_buffer = remainder
                    break

                reasoning_text = buffer[:closing_index]
                if reasoning_text:
                    reasoning_parts.append(reasoning_text)
                    self.transcript.raw_buffer += reasoning_text
                    self.transcript.normalized_buffer += reasoning_text
                self.transcript.pending_buffer = buffer[closing_index + len(CLOSE_TAG) :]
                self.transcript.open_segment = False
                continue

            opening_index = buffer.find(OPEN_TAG)
            closing_index = buffer.find(CLOSE_TAG)

            if closing_index != -1 and (opening_index == -1 or closing_index < opening_index):
                reasoning_text = buffer[:closing_index]
                if reasoning_text:
                    reasoning_parts.append(reasoning_text)
                    self.transcript.raw_buffer += reasoning_text
                    self.transcript.normalized_buffer += reasoning_text
                self.transcript.pending_buffer = buffer[closing_index + len(CLOSE_TAG) :]
                continue

            if opening_index == -1:
                if final:
                    answer_text = buffer
                    remainder = ""
                else:
                    suffix = _incomplete_tag_suffix(buffer, tags)
                    remainder = suffix
                    answer_text = buffer[: len(buffer) - len(remainder)] if remainder else buffer
                if answer_text:
                    answer_parts.append(answer_text)
                    self.transcript.answer_buffer += answer_text
                self.transcript.pending_buffer = remainder
                break

            answer_text = buffer[:opening_index]
            if answer_text:
                answer_parts.append(answer_text)
                self.transcript.answer_buffer += answer_text
            self.transcript.pending_buffer = buffer[opening_index + len(OPEN_TAG) :]
            self.transcript.open_segment = True

        return "".join(answer_parts), "".join(reasoning_parts)
