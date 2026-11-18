import pandas as pd
from persona_engine.hf_loader import numeric_ocean_columns, map_ocean_record

def test_numeric_ocean_columns():
    frame = pd.DataFrame({"O": [0.2, 0.8], "C": [0.3, 0.7], "text": ["a", "b"], "bad": [2, 3]})
    assert numeric_ocean_columns(frame) == ["O", "C"]

def test_map_ocean_record():
    row = pd.Series({"O": 0.1, "C": 0.2, "E": 0.3, "A": 0.4, "N": 0.5})
    mapped = map_ocean_record(row, {
        "openness":"O", "conscientiousness":"C", "extraversion":"E",
        "agreeableness":"A", "neuroticism":"N"
    })
    assert mapped["neuroticism"] == 0.5
