# Meetly audio samples

Mixed-language test conversations for the Meetly lab app (MEE-1330). The app reads `manifest.json` to list them, downloads `audio/<id>.wav` (16 kHz mono) and keeps the ground truth `truth/<id>.json` (start, end, language, text per turn) for scoring.

Lengths: short (< 1 min), medium (1-5 min: Indian, European and Asian pairs with English, india-5, world-8), long (>= 5 min: en-hi-long, en-only-long). Each turn is one sentence by a different FLEURS speaker: these test language routing and accuracy, not speaker memory or code-switching inside a sentence. Add real recordings later as audio/ + truth/ + a manifest entry.

Rebuild: `python3 -I build_samples.py <fleurs-dir> .`

## Licence

Audio and transcripts: FLEURS test split, Google, CC-BY 4.0 (https://huggingface.co/datasets/google/fleurs). Clips are joined with 0.6 s of silence; no other changes.

## Real recordings

Seven real-speech samples: two AMI meetings (CC BY 4.0, 10 and 30 min, 4-5 speakers), two MUCS 2021 Hindi-English lectures (CC BY-SA 4.0, one speaker, natural code-switching), an ASCEND Mandarin-English chat (CC BY-SA 4.0, 2 speakers; utterances joined per speaker), and VoxPopuli German and French plenary segments (CC0). Each manifest entry names its source and licence; `scripts/real/` rebuilds them. Turns tagged `hi+en` / `zh+en` mix both languages.
