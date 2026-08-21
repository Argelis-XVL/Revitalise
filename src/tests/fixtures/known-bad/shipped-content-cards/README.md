# known-bad fixture — `shipped-content` check 4 (card drift)

`borderline-card-drifted.json` is `docs/development/cards/borderline-card.json` with one word
changed in the first `TextBlock`. Nothing else differs, and the file is valid JSON — which is the
whole point: every other gate in the build passes it.

Prove the gate can fail:

```bash
python3 scripts/verify-shipped-content.py src/solutions/RevitaliseGrantAutomation \
    --cards src/tests/fixtures/known-bad/shipped-content-cards
```

Expected: exit 1, naming the drifted file, because it matches no `body/messageBody` string
actually shipped in a flow definition.

`IMP-0131`. The defect this models is not hypothetical: the daily-summary `notes.md` still said
"THIS IS NOT AN ADAPTIVE CARD" a full day after the card shipped, because nothing tied the
readable copy to the shipped one.
