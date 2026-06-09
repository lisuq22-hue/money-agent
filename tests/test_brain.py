import pytest
from agent.brain import Brain


class TestBrain:
    def setup_method(self):
        self.brain = Brain(api_key="test_key")

    def test_fallback_cleanup_when_disk_full(self):
        result = self.brain._fallback_think({"resources": {"disk_gb": 30}})
        assert result["action"] == "cleanup"

    def test_fallback_explore_when_no_income(self):
        result = self.brain._fallback_think({
            "finance": {"income": 0},
            "network": {"github_reachable": True},
        })
        assert result["action"] == "explore_channels"

    def test_fallback_no_repeat(self):
        self.brain._action_history = [
            {"time": "", "action": "self_check", "reason": ""},
            {"time": "", "action": "self_check", "reason": ""},
        ]
        result = self.brain._fallback_think({})
        assert result["action"] != "self_check"

    def test_build_prompt(self):
        ctx = {
            "resources": {"cpu": 25, "memory_mb": 500, "disk_gb": 5},
            "network": {"github_reachable": True, "google_reachable": False},
            "finance": {"income": 50, "expense": 10, "profit": 40},
            "recent_actions": [],
            "memory_summary": "ok",
            "knowledge_count": 3,
            "current_time": "2026-06-09",
        }
        prompt = self.brain._build_prompt(ctx)
        assert "CPU" in prompt
        assert "50" in prompt

    def test_parse_valid_json(self):
        result = self.brain._parse_response(
            '{"action": "self_check", "reason": "t", "urgency": 5, "rest_seconds": 300}'
        )
        assert result["action"] == "self_check"

    def test_parse_malformed(self):
        result = self.brain._parse_response("not json")
        assert "action" in result

    def test_action_history(self):
        self.brain._action_history = [{"time": "", "action": "rest", "reason": ""}]
        assert len(self.brain.get_action_history()) == 1

    def test_rest_seconds_range(self):
        result = self.brain._fallback_think({})
        assert 60 <= result["rest_seconds"] <= 7200

    def test_valid_actions(self):
        valid = ["self_check", "evolve_code", "explore_channels", "engage_community",
                 "analyze_finance", "learn", "register_platform", "cleanup", "rest"]
        for ctx in [{}, {"resources": {"disk_gb": 30}}, {"finance": {"income": 0}, "network": {"github_reachable": True}}]:
            result = self.brain._fallback_think(ctx)
            assert result["action"] in valid
