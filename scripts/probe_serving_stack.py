"""Block E decision 3: ONE chat call, to find out what the gateway will tell us
about which stack served it.

Why a probe and not a field
---------------------------

`BLOCK_E_START` asks for a `system_fingerprint` beside `model` and calls it
"one line". It is not one line, and it may not be anything at all:

  * `_chat` returns a three-tuple and has six call sites plus two in the test
    suite. The last time its arity moved, one call site was missed and every
    live answer call raised ValueError for five days. That is why the recording
    went in as an out-parameter — see `answer/translate.py`.

  * `system_fingerprint` is an OpenAI field. This gateway fronts Anthropic,
    whose API does not return one. LiteLLM may pass through a null, or omit it,
    or synthesise something.

A field that reads null on all 270 calls is the fourth vacuous proof in five
days — BLOCK_E_START carries the first three as trap 4, and `D4_RESULT.md`
records what the last one cost. So `_serving_stack` records only keys that are
actually populated, and this probe is how we find out, ONCE and for one chat
call, which those are. Run it BEFORE day 1: the answer belongs in the result
document either way, and "the gateway returns nothing distinguishing" is a
finding worth stating rather than a column worth adding.

Needs the gateway up and .env loaded, exactly as a sweep does:

    python scripts/probe_serving_stack.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# A script under scripts/ is run as `python scripts\probe_serving_stack.py`,
# which puts scripts/ on sys.path and NOT the repository root - so `from answer
# import translate` raises ModuleNotFoundError before a single chat call is
# made. Every other script here that imports a repository package does exactly
# this line; see scripts/probe_rerank.py:22. Missed on 2026-08-26 because the
# offline suites import the packages directly and never exercise this path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# FINDING 10: this process's own stdout. On Windows `print` writes through a
# stream whose encoding comes from the console code page, and through a PIPE or
# a REDIRECT it falls back to the locale codec — cp1252, which cannot encode
# Greek, Tamil, Chinese, Ge'ez or runic. It does not degrade: it raises
# UnicodeEncodeError mid-output, with the file half written and every number in
# it correct. Found 2026-08-22 at build_ui_data.py:730, printing the Greek behind
# a `case_only` span into a redirect.
#
# Two neighbouring boundaries were already guarded and are NOT this one: a CHILD
# process's stdout (PYTHONIOENCODING in its env) and a PARENT decoding that child
# (subprocess encoding=). Both are about a pipe between two processes. This is
# about where THIS process is writing, and until 2026-08-22 nothing anywhere
# guarded it.
#
# errors="replace" is deliberate. A harness that cannot encode one character
# should print a replacement character and finish; it should never lose a run to
# a formatting problem. A mangled character is cosmetic. A three-day sweep that
# dies on day one is ninety chat calls.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass


def main() -> int:
    from answer import translate

    # CORRECTED 2026-08-28, Block E correction 4. This sent
    # `resolve_model_label()` — the CONCRETE model name, read by that function
    # out of gateway/config.yaml on this disk — and so made a request no sweep
    # has ever made. The gateway echoed the concrete name straight back, and
    # two probe readings either side of Block E were reported as evidence that
    # the serving stack had not moved. They were evidence about a request shape
    # the sweeps do not use, carrying a value that came from a file in this
    # repository rather than from the provider.
    #
    # A sweep calls assemble with no `model=`, so `_chat` gets DEFAULT_MODEL
    # and every one of the 396 Block E archives carries `"model":
    # "chat-default"`. Send that, so this probe measures the path the archives
    # were made on. If LiteLLM ever returns the RESOLVED name through the
    # alias, this becomes a real drift detector; if it echoes `chat-default`,
    # the null result is confirmed where it matters.
    alias = translate.DEFAULT_MODEL
    resolved = translate.resolve_model_label()
    print(f"one chat call through the gateway alias {alias!r}")
    print(f"gateway/config.yaml on this disk points that at {resolved!r} — "
          f"read locally, NOT confirmed by the gateway\n")

    provenance: dict = {}
    try:
        text, retries, temperature = translate._chat(
            [{"role": "user", "content": "Reply with the single word: ok"}],
            model=alias, max_tokens=16, provenance=provenance,
        )
    except Exception as exc:  # noqa: BLE001 — provider errors are untyped
        print(f"the call failed: {exc}", file=sys.stderr)
        print("\nThe gateway must be up and .env loaded in THIS window, the "
              "same as for a sweep.", file=sys.stderr)
        return 2

    print(f"answer      {text.strip()[:60]!r}  "
          f"(retries {retries}, temperature {temperature})")
    print("\nwhat _serving_stack recorded for THIS call, made through the same "
          "alias a sweep\nuses:\n")
    print(json.dumps(provenance, indent=2, ensure_ascii=False))
    identity = translate.serving_stack_identity(provenance)
    print("\nand what of that could identify a STACK, once the per-call `id` "
          "and the echoed\n`model` are removed (Block E corrections 3 and 4):\n")
    print(json.dumps(identity, indent=2, ensure_ascii=False))
    if provenance and not identity:
        print("\n  EMPTY IDENTITY. Everything the gateway returned is either "
              "unique to this call\n  or an echo of what was sent. The sweep's "
              "'N distinct stacks' line counts this\n  correctly as none.")

    if not provenance:
        print(
            "\nEMPTY. The gateway returned nothing distinguishing.\n"
            "  This is decision 3's answer and it belongs in the result "
            "document as a stated\n  limit: provider-side drift and sampling "
            "variance cannot be told apart in these\n  archives, so FINDING "
            "18's question stays open for a reason that is written\n  down "
            "rather than for one nobody noticed. No null column is added.\n"
            "  Do NOT chase a fourth vacuous proof - see BLOCK_E_START trap 4."
        )
        return 1

    if "system_fingerprint" not in provenance:
        print(
            "\nNo `system_fingerprint` - it is an OpenAI field and this "
            "gateway fronts\n  Anthropic. What IS above is recorded, and the "
            "absence is the finding.\n  Say in the result document which keys "
            "were available, so that a later reader\n  knows the archive "
            "carries what there was and not what was wanted."
        )
    print(
        "\nWhat two readings either side of a block are worth, honestly: only "
        "as much as\nthe IDENTITY above carries. If that is empty, two "
        "identical readings are two\nidentical echoes and say nothing about "
        "the stack - which is what happened across\nBlock E, where the probe "
        "additionally sent the concrete model name instead of\nthe alias and "
        "so never touched the sweep path at all (correction 4). If a key in\n"
        "the IDENTITY ever changes between days, THAT is the answer FINDING 18 "
        "asked for."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
