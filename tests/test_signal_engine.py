from lakehouse.config import LakehouseConfig
from lakehouse.signal_engine import SignalEngine, SignalWeights


def test_default_weights_diverge_as_documented():
    """README discloses the library defaults diverge from the deployed composite."""
    weights = SignalWeights()
    assert (weights.grade, weights.cost, weights.production, weights.growth, weights.esg) == (
        0.25,
        0.25,
        0.20,
        0.15,
        0.15,
    )
    assert abs(weights.grade + weights.cost + weights.production + weights.growth + weights.esg - 1.0) < 1e-6
    config = LakehouseConfig()
    assert (config.grade_weight, config.cost_weight, config.production_weight, config.growth_weight, config.esg_weight) == (
        0.25,
        0.25,
        0.20,
        0.15,
        0.15,
    )


def test_weighted_composite_matches_manual_calculation():
    engine = SignalEngine()
    signal = engine.compute_signal("X001", "X Co", "2024Q1", 80, 60, 70, 90, 50)
    expected = round(0.25 * 80 + 0.25 * 60 + 0.20 * 70 + 0.15 * 90 + 0.15 * 50, 2)
    assert signal.weighted_signal == expected == 70.0
    assert signal.tier == "B"


def test_scores_clamped_and_tier_boundaries():
    engine = SignalEngine()
    clamped = engine.compute_signal("X001", "X Co", "2024Q1", 150, -5, 0, 0, 0)
    assert clamped.grade_score == 100.0
    assert clamped.cost_score == 0.0
    assert clamped.weighted_signal == 25.0  # 0.25 * 100 with library weights
    assert clamped.tier == "D"
    assert SignalEngine._classify_tier(80) == "A"
    assert SignalEngine._classify_tier(65) == "B"
    assert SignalEngine._classify_tier(50) == "C"
    assert SignalEngine._classify_tier(49.9) == "D"
