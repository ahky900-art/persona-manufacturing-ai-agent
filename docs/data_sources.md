# Data source and provenance notes

## NVIDIA Nemotron-Personas-Korea (Hugging Face base dataset)

- Dataset: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea
- Dataset card: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea/blob/main/README.md
- License shown on Hugging Face: CC BY 4.0.
- The base dataset has 26 fields and includes professional persona, persona summary, skills and expertise, occupation and contextual fields. It does **not** expose the five OCEAN attributes in its published base schema.
- The dashboard streams only a bounded sample (default 500 records) instead of downloading the full 1M-row dataset.
- Since the base schema has no OCEAN values, it uses a transparent keyword-based fallback to propose a *review lens*. It must not be described as OCEAN/MBTI classification.

## NVIDIA Nemotron-Personas-Korea-Extended

- NVIDIA NGC resource: https://catalog.ngc.nvidia.com/orgs/nvidia/nemotron-personas/resources/nemotron-personas-dataset-ko_kr/-
- NVIDIA's published Extended schema documents five OCEAN fields (`openness`, `conscientiousness`, `extraversion`, `agreeableness`, `neuroticism`) as descriptive strings with scores/labels/explanations.
- NGC access and download may require sign-in. This app does not pretend the Extended data is available through the base Hugging Face dataset ID.
- If the user has a licensed/downloaded Extended CSV, upload it in Persona Lab. The app parses explicit scores/labels and uses OCEAN only when all five traits are interpretable.
- If the values cannot be parsed, the system does not invent missing traits; it falls back to text-based review-lens classification.
- Only work/persona/OCEAN fields are retained by the upload loader. Name, sex, age, health, family, income and other demographic/health fields are excluded from the analysis frame.

## KOSHA manufacturing accident cases

- Public data page: https://www.data.go.kr/data/15163146/fileData.do
- Dataset title: 한국산업안전보건공단_산업재해 사례(업무상 사고사례)_20260903
- The public data description identifies 1,136 manufacturing accident case records and provides these columns:
  - `BBSCTT_SJ_NM`: accident title
  - `BBSCTT_CN`: accident description
  - `DSSTR_INDUCT_FCTR_CN`: accident cause
  - `RSKNSS_DCRS_CNTRPLN_CN`: prevention / risk reduction measures
- The CSV loader maps these source columns to the app's normalized title, description, cause and prevention fields.
- Download the official CSV from the public data page and upload it in the Accident Knowledge tab. The app does not bypass portal access controls or claim to fetch the file automatically.
- Keep the original file unchanged. Record source URL, download date, dataset title, license/terms, and any transformations in a separate provenance record. Follow the dataset's current attribution and redistribution conditions.
- The included CSV is fabricated demonstration content and is not an official KOSHA extract.

## Data separation

| Data class | Intended use | Must not be used for |
|---|---|---|
| Synthetic persona | Review-lens exploration | Predicting an individual worker's accident probability |
| Historical accident narratives | Hazard and control knowledge retrieval | Direct real-time probability estimation |
| Normal-operation and sensor records | Future real-time state detection after validation | Unreviewed automated safety decisions |
