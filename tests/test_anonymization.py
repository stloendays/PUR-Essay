import pandas as pd

from pur_agent.anonymization import anonymize_candidate_table


def test_deterministic_and_seed_sensitive(toy_table, toy_config):
    a = anonymize_candidate_table(toy_table, toy_config, seed=7)
    b = anonymize_candidate_table(toy_table, toy_config, seed=7)
    c = anonymize_candidate_table(toy_table, toy_config, seed=8)
    assert a.blind_table.equals(b.blind_table)
    assert a.candidate_forward == b.candidate_forward
    assert a.candidate_forward != c.candidate_forward


def test_names_and_answer_columns_hidden(toy_table, toy_config):
    a = anonymize_candidate_table(toy_table, toy_config, seed=7)
    text = a.blind_table.to_csv(index=False)
    assert "T_0001" not in text and "oracle_rank" not in text and "gold_candidate_id" not in text
    assert "X:50" not in text and "Y:50" not in text
    assert "Polyol_A" in text and "Polyol_B" in text
    assert set(a.material_reverse.values()) == {"X", "Y"}
    assert {"Polyol_A_parts", "Polyol_B_parts"} <= set(a.blind_table.columns)


def test_reverse_mapping_round_trip(toy_table, toy_config):
    a = anonymize_candidate_table(toy_table, toy_config, seed=7)
    for old, new in a.candidate_forward.items():
        assert a.candidate_reverse[new] == old
    ids = a.blind_table["source_candidate_id"].tolist()
    assert sorted(ids) == sorted(f"Candidate_{i:04d}" for i in range(1, len(toy_table) + 1))
    restored = a.blind_table["source_candidate_id"].map(a.candidate_reverse)
    assert set(restored) == set(toy_table["source_candidate_id"])


def test_blend_rewrite_does_not_touch_substrings():
    df = pd.DataFrame({"candidate_id": ["a", "b"], "blend": ["PPG100:50+PPG1000:50"] * 2, "PPG100": [50, 50], "PPG1000": [50, 50],
                       "eta80": [1, 1], "eta120": [1, 1], "ratio": [1, 1], "nco_oh": [1, 1], "mdi_parts": [1, 1]})
    cfg = {"columns": {"candidate_id": "candidate_id", "blend": "blend"}, "anonymization": {"component_columns": ["PPG100", "PPG1000"]}}
    a = anonymize_candidate_table(df, cfg, seed=1)
    blend = a.blind_table["blend"].iloc[0]
    assert blend.count("Polyol_") == 2 and "PPG" not in blend
