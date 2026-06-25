import json


class ConfidenceScorer:

    def __init__(self, config_path, pattern_memory_path):

        with open(config_path, "r") as f:
            self.config = json.load(f)

        with open(pattern_memory_path, "r") as f:
            self.pattern_memory = json.load(f)

    def get_kb_similarity(self, kb_references):

        if not kb_references:
            return 0.0

        return max(
            kb.get("similarity", 0.0)
            for kb in kb_references
        )

    def get_action_safety(self, action):

        safe_actions = self.config["safe_actions"]

        action_lower = action.lower()

        for safe_action in safe_actions:
            if safe_action in action_lower:
                return 1.0

        return 0.4

    def get_severity_factor(self, severity):

        mapping = {
            "P1": 0.0,
            "P2": 0.7,
            "P3": 1.0,
            "P4": 1.0
        }

        return mapping.get(severity, 0.4)

    def get_pattern_memory(
        self,
        tower,
        incident_type,
        affected_ci
    ):

        key = f"{tower}:{incident_type}:{affected_ci}"

        successes = self.pattern_memory.get(key, 0)

        return min(successes * 0.25, 1.0)

    def get_kb_coverage(self, kb_references):

        return 1.0 if kb_references else 0.3

    def calculate(self, reasoning_output):

        classification = reasoning_output["classification"]

        tower = classification["tower"]
        incident_type = classification["type"]
        severity = classification["severity"]
        affected_ci = classification["affected_ci"]

        action = reasoning_output["recommended_action"]

        kb_refs = reasoning_output.get(
            "kb_references",
            []
        )

        kb_similarity = self.get_kb_similarity(
            kb_refs
        )

        action_safety = self.get_action_safety(
            action
        )

        severity_factor = self.get_severity_factor(
            severity
        )

        pattern_memory = self.get_pattern_memory(
            tower,
            incident_type,
            affected_ci
        )

        kb_coverage = self.get_kb_coverage(
            kb_refs
        )

        weights = self.config["weights"]

        score = (
            kb_similarity * weights["kb_similarity"]
            + action_safety * weights["action_safety"]
            + severity_factor * weights["severity_factor"]
            + pattern_memory * weights["pattern_memory"]
            + kb_coverage * weights["kb_coverage"]
        )

        score = round(score, 2)

        if severity == "P1":
            decision = "handoff"

        elif score >= self.config["thresholds"]["auto"]:
            decision = "auto"

        elif score >= self.config["thresholds"]["approve"]:
            decision = "approve"

        else:
            decision = "handoff"

        return {
            "confidence": {
                "score": score,
                "decision": decision,
                "signals": {
                    "kb_similarity": round(
                        kb_similarity,
                        2
                    ),
                    "action_safety": round(
                        action_safety,
                        2
                    ),
                    "severity_factor": round(
                        severity_factor,
                        2
                    ),
                    "pattern_memory": round(
                        pattern_memory,
                        2
                    ),
                    "kb_coverage": round(
                        kb_coverage,
                        2
                    )
                }
            }
        }