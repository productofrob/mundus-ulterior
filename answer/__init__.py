"""In-loop translation and grounded answer assembly (Phase 1, Parts 6-7).

Part 6 lives here: translating a retrieved non-English chunk into English, then
translating that English back into the source language *without letting the
model see the original*, and scoring the round trip. The score is what Part 7
will use to decide how much weight a machine translation may carry next to a
published one.
"""
