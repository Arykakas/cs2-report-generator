import polars as pl
import sys
import os

# Add the project root to sys.path so we can import from cs2_report
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cs2_report.analysis.hits import analyze_hits
from cs2_report.analysis.aim import analyze_aim

class MockDemo:
    def __init__(self):
        # Mock damages DataFrame
        self.damages = pl.DataFrame({
            "attacker_steamid": [12345, 67890],
            "victim_steamid": [67890, 12345],
            "hit_model_data": ["head", "chest"],
            "weapon": ["weapon_ak47", "weapon_m4a1"]
        })
        
        # Mock kills DataFrame
        self.kills = pl.DataFrame({
            "attacker_steamid": [12345],
            "victim_steamid": [67890],
            "tick": [1000],
            "victim_name": "VictimPlayer",
            "weapon": ["weapon_ak47"]
        })

        # Mock shots DataFrame - Fixed heights
        self.shots = pl.DataFrame({
            "steamid": [12345, 12345],
            "tick": [900, 1000],
            "x": [100, 200],
            "y": [200, 300],
            "z": [500, 600],
            "yaw": [45, 90],
            "pitch": [10, 20],
            "weapon": ["weapon_ak47", "weapon_ak47"]
        })

    def load(self, table_name):
        # Mock the .load() method used in hits.py
        if table_name == "damages":
            return self

def test_analysis():
    demo = MockDemo()
    player_id = 12345
    
    print("Testing analyze_hits...")
    try:
        hit_results = analyze_hits(demo, player_id)
        print(f"analyze_hits success! Keys: {list(hit_results.keys())}")
        print(f"hit_model_data: {hit_results.get('hit_model_data')}")
    except Exception as e:
        print(f"analyze_hits failed with error: {e}")
        import traceback
        traceback.print_exc()

    print("Testing analyze_aim...")
    try:
        # Mocking the specific inputs required by analyze_aim
        # angular_velocity_by_tick and angular_deviation_by_tick are dicts mapping tick -> float
        mock_angular_vel = {900: 10.0, 1000: 5.0}
        mock_angular_dev = {900: 1.0, 1000: 2.0}
        
        # target_shots is a DataFrame of shots for the player
        target_shots = demo.shots.filter(pl.col("steamid") == player_id)
        
        aim_results = analyze_aim(
            demo,
            target_shots,
            player_id,
            mock_angular_vel,
            mock_angular_dev,
            demo.shots.filter(pl.col("steamid") == player_id) # shots_with_velocity
        )
        print(f"analyze_aim success! Keys: {list(aim_results.keys())}")
        print(f"average_kill_deviation: {aim_results.get('average_kill_deviation')}")
    except Exception as e:
        print(f"analyze_aim failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis()