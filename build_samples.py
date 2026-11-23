"""Build the Meetly sample library: mixed-language conversations from the
FLEURS test split (Google, CC-BY 4.0) at several lengths, each with its
ground truth (start, end, language, text per turn) and one manifest.json the
lab app reads to discover and download them (MEE-1330).

    python3 -I tools/bench/samples.py .bench/fleurs <out-dir>

<out-dir> gets audio/<id>.wav, truth/<id>.json and manifest.json. Each FLEURS
clip is a different speaker reading one sentence, so a sample tests language
routing and accuracy, not speaker memory or code-switching within a sentence.
"""
import array, hashlib, json, os, sys, wave

src, out = sys.argv[1], sys.argv[2]
for d in ("audio", "truth"):
    os.makedirs(f"{out}/{d}", exist_ok=True)

L = {"en": "en_us", "hi": "hi_in", "ta": "ta_in", "de": "de_de", "es": "es_419", "fr": "fr_fr", "ru": "ru_ru",
     "ko": "ko_kr", "ja": "ja_jp", "zh": "cmn_hans_cn", "ar": "ar_eg", "th": "th_th", "vi": "vi_vn", "id": "id_id",
     "pt": "pt_br", "bn": "bn_in", "pa": "pa_in", "ml": "ml_in", "ur": "ur_pk", "mr": "mr_in"}
NAMES = {"en": "English", "hi": "Hindi", "ta": "Tamil", "de": "German", "es": "Spanish", "fr": "French",
         "ru": "Russian", "ko": "Korean", "ja": "Japanese", "zh": "Chinese", "ar": "Arabic", "th": "Thai",
         "vi": "Vietnamese", "id": "Indonesian", "pt": "Portuguese", "bn": "Bengali", "pa": "Punjabi",
         "ml": "Malayalam", "ur": "Urdu", "mr": "Marathi"}

# (id, languages in turn order, number of turns). Turns cycle through the
# languages; about 10 s each, so 4 turns ≈ 40 s, 12 ≈ 2 min, 40 ≈ 7 min.
SAMPLES = [
    ("en-hi-short", ["en", "hi"], 4),
    ("en-hi", ["en", "hi"], 12),
    ("en-hi-long", ["en", "hi"], 40),
    ("en-only-long", ["en"], 30),
    ("hi-only", ["hi"], 12),
    ("hi-ta", ["hi", "ta"], 10),
    ("hi-bn", ["hi", "bn"], 10),
    ("en-ta", ["en", "ta"], 10),
    ("en-pa", ["en", "pa"], 10),
    ("en-ml", ["en", "ml"], 10),
    ("en-mr", ["en", "mr"], 10),
    ("en-ur", ["en", "ur"], 10),
    ("en-de", ["en", "de"], 10),
    ("en-es", ["en", "es"], 10),
    ("en-fr", ["en", "fr"], 10),
    ("de-fr", ["de", "fr"], 10),
    ("en-ru", ["en", "ru"], 10),
    ("en-pt", ["en", "pt"], 10),
    ("zh-en", ["zh", "en"], 8),
    ("ja-en", ["ja", "en"], 8),
    ("ko-en", ["ko", "en"], 8),
    ("ar-en", ["ar", "en"], 8),
    ("th-en", ["th", "en"], 8),
    ("vi-en", ["vi", "en"], 8),
    ("id-en", ["id", "en"], 8),
    ("india-5", ["en", "hi", "ta", "bn", "pa"], 15),
    ("world-8", ["en", "hi", "de", "es", "zh", "ja", "ar", "ru"], 16),
]

meta = {l: json.load(open(f"{src}/{l}/meta.json")) for l in os.listdir(src) if os.path.isfile(f"{src}/{l}/meta.json")}
used = {l: 0 for l in meta}
gap = array.array("h", [0] * (16000 * 6 // 10))
manifest = []
for sid, langs, n in SAMPLES:
    if any(L[x] not in meta for x in langs):
        print("skip", sid, "(missing FLEURS clips)")
        continue
    pcm, t, turns = array.array("h"), 0.0, []
    for i in range(n):
        code = langs[i % len(langs)]
        clips = meta[L[code]]
        c = clips[used[L[code]] % len(clips)]
        used[L[code]] += 1
        with wave.open(f"{src}/{L[code]}/{c['file']}") as w:
            assert w.getframerate() == 16000 and w.getnchannels() == 1 and w.getsampwidth() == 2, c["file"]
            a = array.array("h", w.readframes(w.getnframes()))
        turns.append({"start": round(t, 2), "end": round(t + len(a) / 16000, 2), "lang": code,
                      "fleurs": L[code], "file": c["file"], "gender": c["gender"], "text": c["raw"]})
        pcm += a
        pcm += gap
        t += (len(a) + len(gap)) / 16000
    wav = f"{out}/audio/{sid}.wav"
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(pcm.tobytes())
    json.dump({"id": sid, "duration_sec": round(t, 1), "source": "FLEURS test split (Google, CC-BY 4.0)",
               "turns": turns}, open(f"{out}/truth/{sid}.json", "w"), ensure_ascii=False, indent=1)
    data = open(wav, "rb").read()
    mins = t / 60
    length = "short" if t < 60 else "long" if t >= 300 else "medium"
    title = " + ".join(NAMES[x] for x in langs) if len(langs) <= 3 else f"{len(langs)} languages ({' '.join(langs)})"
    manifest.append({
        "id": sid,
        "title": f"{title} · {mins:.0f} min" if mins >= 1 else f"{title} · {t:.0f} s",
        "languages": langs,
        "duration_sec": round(t, 1),
        "turns": n,
        "length": length,
        "audio": f"audio/{sid}.wav",
        "truth": f"truth/{sid}.json",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    })
    print(f"{sid:14s} {t:6.0f} s  {n:3d} turns  {len(data) / 1e6:5.1f} MB")

json.dump({"version": 1,
           "about": "Mixed-language test conversations for Meetly. Built by tools/bench/samples.py (MEE-1330).",
           "license": "Audio and transcripts: FLEURS test split, Google, CC-BY 4.0 "
                      "(https://huggingface.co/datasets/google/fleurs). Each turn is a different FLEURS speaker.",
           "samples": manifest}, open(f"{out}/manifest.json", "w"), ensure_ascii=False, indent=1)
print(len(manifest), "samples,", round(sum(s["bytes"] for s in manifest) / 1e6), "MB")
