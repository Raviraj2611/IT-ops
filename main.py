import json

from scorer import ConfidenceScorer


def main():

    scorer = ConfidenceScorer(
        config_path="config.json",
        pattern_memory_path="pattern_memory.json"
    )

    with open(
        "sample/reasoning_output.json",
        "r"
    ) as f:

        test_cases = json.load(f)

    for case in test_cases:

        print("\n" + "=" * 70)
        print(f"TEST CASE : {case['test_name']}")
        print("=" * 70)

        result = scorer.calculate(case)

        print(
            json.dumps(
                result,
                indent=2
            )
        )


if __name__ == "__main__":
    main()