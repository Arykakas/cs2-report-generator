import unittest

from cs2_report.analysis.archetype import (
    build_archetype_result,
    calculate_tie_aware_ranks,
    generate_narrative,
    normalize_narrative_stats,
    select_archetype,
    select_side_comparison,
)


class TieAwareRankingTests(unittest.TestCase):
    def test_all_equal_values_are_one_tied_leader(self):
        ranking = calculate_tie_aware_ranks([50.0, 50.0, 50.0], higher_is_better=True)
        self.assertEqual(ranking["ranks"], {50.0: 1})
        self.assertEqual(ranking["relative_scores"], {50.0: 100.0})
        self.assertEqual(ranking["leader_flags"], {50.0: True})
        self.assertEqual(ranking["tied_leaders"], {50.0})

    def test_high_values_have_equal_dense_rank_and_shared_leader(self):
        ranking = calculate_tie_aware_ranks([90.0, 90.0, 70.0], higher_is_better=True)
        self.assertEqual(ranking["ranks"], {90.0: 1, 70.0: 2})
        self.assertAlmostEqual(ranking["relative_scores"][90.0], 100.0)
        self.assertAlmostEqual(ranking["relative_scores"][70.0], 0.0)
        self.assertEqual(ranking["leader_flags"], {90.0: True, 70.0: False})
        self.assertEqual(ranking["tied_leaders"], {90.0})

    def test_low_values_are_ranked_lowest_first(self):
        ranking = calculate_tie_aware_ranks([20.0, 10.0, 10.0], higher_is_better=False)
        self.assertEqual(ranking["ranks"], {10.0: 1, 20.0: 2})
        self.assertAlmostEqual(ranking["relative_scores"][10.0], 100.0)
        self.assertAlmostEqual(ranking["relative_scores"][20.0], 0.0)
        self.assertEqual(ranking["tied_leaders"], {10.0})

    def test_single_player_is_the_only_leader(self):
        ranking = calculate_tie_aware_ranks([42.0], higher_is_better=True)
        self.assertEqual(ranking["ranks"], {42.0: 1})
        self.assertEqual(ranking["relative_scores"], {42.0: 100.0})
        self.assertEqual(ranking["tied_leaders"], {42.0})

    def test_missing_values_have_no_ranking(self):
        ranking = calculate_tie_aware_ranks([], higher_is_better=True)
        self.assertEqual(ranking["ranks"], {})
        self.assertEqual(ranking["relative_scores"], {})
        self.assertEqual(ranking["tied_leaders"], set())


class ArchetypeCombinationTests(unittest.TestCase):
    def test_aggressive_and_precise_combination(self):
        result = select_archetype({
            "aggression": 90,
            "precision": 85,
            "utility": 40,
            "positioning": 50,
            "availability": {"eligible": True},
        })
        self.assertEqual(result["archetype"], "The Aggressive Marksman")

    def test_aggressive_low_precision_is_rusher(self):
        result = select_archetype({
            "aggression": 90,
            "precision": 40,
            "utility": 40,
            "positioning": 50,
            "availability": {"eligible": True},
        })
        self.assertEqual(result["archetype"], "The High-Octane Rusher")

    def test_passive_precise_is_patient_marksman(self):
        result = select_archetype({
            "aggression": 40,
            "precision": 90,
            "utility": 40,
            "positioning": 50,
            "availability": {"eligible": True},
        })
        self.assertEqual(result["archetype"], "The Patient Marksman")

    def test_utility_and_positioning_are_tactical_anchor(self):
        result = select_archetype({
            "aggression": 40,
            "precision": 50,
            "utility": 90,
            "positioning": 85,
            "availability": {"eligible": True},
        })
        self.assertEqual(result["archetype"], "The Tactical Anchor")

    def test_tied_leaders_preserve_multiple_distinctions(self):
        result = select_archetype({
            "aggression": 100,
            "precision": 100,
            "utility": 100,
            "positioning": 100,
            "aggression_is_tied_leader": True,
            "precision_is_tied_leader": True,
            "utility_is_tied_leader": False,
            "positioning_is_tied_leader": False,
            "availability": {"eligible": True},
        })
        self.assertEqual(result["tied_distinctions"], ["Aggression", "Precision"])

    def test_insufficient_data_is_explicit(self):
        result = select_archetype({
            "availability": {"eligible": False, "reason": "insufficient_samples"}
        })
        self.assertEqual(result["archetype"], "Insufficient Data")
        self.assertEqual(result["tied_distinctions"], [])


class CanonicalResultTests(unittest.TestCase):
    def test_canonical_builder_preserves_ties_and_narrative_fields(self):
        result = build_archetype_result({
            "aggression": 100,
            "precision": 90,
            "utility": 80,
            "positioning": 50,
            "aggression_is_tied_leader": True,
            "precision_is_tied_leader": False,
            "utility_is_tied_leader": False,
            "positioning_is_tied_leader": False,
            "availability": {"eligible": True},
        }, {"kills": 20, "deaths": 10, "adr": 90})
        self.assertEqual(result["archetype"], "The Aggressive Marksman")
        self.assertEqual(result["tied_distinctions"], ["Aggression"])
        self.assertIn("Playstyle:", result["summary"])


class SideComparisonTests(unittest.TestCase):
    def test_sufficient_ct_and_t_samples_use_side_aware_mode(self):
        result = select_side_comparison([70, 75, 80], [60, 65, 68], minimum_side_samples=3)
        self.assertEqual(result["mode"], "side-aware")

    def test_low_t_sample_falls_back_to_pooled_mode(self):
        result = select_side_comparison([70, 75, 80], [60], minimum_side_samples=3)
        self.assertEqual(result["mode"], "pooled")
        self.assertEqual(result["pooled"], [70, 75, 80, 60])


class NarrativePerformanceTests(unittest.TestCase):
    def test_normalizes_kd_and_adr_bands(self):
        result = normalize_narrative_stats({
            "kills": 18,
            "deaths": 12,
            "adr": 85.0,
        })
        self.assertTrue(result["available"])
        self.assertAlmostEqual(result["kd_ratio"], 1.5)
        self.assertEqual(result["kd_band"], "steady")
        self.assertEqual(result["adr_band"], "high")

    def test_missing_required_stats_are_unavailable(self):
        result = normalize_narrative_stats({"kills": 10, "adr": 70.0})
        self.assertFalse(result["available"])
        self.assertEqual(result["missing"], ["deaths"])

    def test_low_kd_uses_direct_correction_wording(self):
        stats = {"kills": 8, "deaths": 12, "adr": 55.0}
        narrative = generate_narrative("The High-Octane Rusher", {}, stats)
        self.assertIn("Playstyle: The High-Octane Rusher", narrative)
        self.assertIn("Low impact needs direct correction", narrative)
        self.assertIn("K/D is 0.67", narrative)
        self.assertIn("ADR is 55.0", narrative)

    def test_high_performance_acknowledges_playstyle_and_metrics(self):
        stats = {"kills": 20, "deaths": 10, "adr": 90.0}
        narrative = generate_narrative("The Patient Marksman", {}, stats)
        self.assertIn("Playstyle: The Patient Marksman", narrative)
        self.assertIn("strong impact", narrative)
        self.assertIn("K/D is 2.00", narrative)
        self.assertIn("ADR is 90.0", narrative)

    def test_same_aggressive_marksman_tone_changes_with_impact(self):
        poor_stats = {"kills": 8, "deaths": 14, "adr": 55.0}
        strong_stats = {"kills": 20, "deaths": 10, "adr": 90.0}
        poor = generate_narrative("The Aggressive Marksman", {}, poor_stats)
        strong = generate_narrative("The Aggressive Marksman", {}, strong_stats)
        self.assertIn("Playstyle: The Aggressive Marksman", poor)
        self.assertIn("Playstyle: The Aggressive Marksman", strong)
        self.assertIn("Low impact needs direct correction", poor)
        self.assertIn("strong impact", strong)

    def test_narrative_is_deterministic(self):
        stats = {"kills": 15, "deaths": 12, "adr": 72.0}
        first = generate_narrative("The Aggressive Marksman", {}, stats)
        second = generate_narrative("The Aggressive Marksman", {}, stats)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
