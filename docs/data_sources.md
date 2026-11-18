# Data source and provenance notes

## Persona source: NVIDIA Nemotron-Personas-Korea

- Dataset page: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea
- Dataset card and license must be reviewed before use or redistribution.
- The dataset is a synthetic persona resource, not a worker behavior or occupational accident dataset.
- Do not assume an MBTI label exists in the source. This MVP asks the user to inspect the loaded schema and explicitly map five numeric OCEAN columns.
- If OCEAN values are textual, nested, or not normalized to [0,1], the current MVP will not classify them automatically. A source-specific transformation must be documented and validated first.
- Exclude health, sex, age, and other sensitive attributes from worker-level risk scoring.

## Occupational safety source: KOSHA

- KOSHA industrial accident information: https://www.kosha.or.kr/
- Serious industrial accident case archive and manufacturing case datasets may have distinct access, attribution, and redistribution terms.
- Keep the original file unchanged. Record source URL, download date, dataset title, license/terms, and any transformations in a separate provenance record.
- The included CSV is fabricated demonstration content and is not an official KOSHA extract.

## Data separation

| Data class | Intended use | Must not be used for |
|---|---|---|
| Synthetic persona | Review-lens exploration | Predicting an individual worker's accident probability |
| Historical accident narratives | Hazard and control knowledge retrieval | Direct real-time probability estimation |
| Normal-operation and sensor records | Future real-time state detection after validation | Unreviewed automated safety decisions |
