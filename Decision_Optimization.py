import csv
from datetime import datetime


# ============================================================
#                 DECISION OPTIMIZATION TOOL
# ============================================================

WIDTH = 85


def print_header(title):
    """Display a formatted section heading."""
    print("\n" + "=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)


def get_integer(message, minimum=1):
    """Get a valid integer from the user."""
    while True:
        try:
            value = int(input(message))

            if value >= minimum:
                return value

            print(f"Please enter an integer >= {minimum}.")

        except ValueError:
            print("Invalid input. Please enter a whole number.")


def get_non_empty_text(message):
    """Get non-empty text."""
    while True:
        value = input(message).strip()

        if value:
            return value

        print("Input cannot be empty.")


def get_positive_float(message):
    """Get a positive numerical value."""
    while True:
        try:
            value = float(input(message))

            if value > 0 and value != float("inf"):
                return value

            print("Value must be greater than zero.")

        except ValueError:
            print("Please enter a valid number.")


def get_score(message):
    """Get a score between 1 and 10."""
    while True:
        try:
            value = float(input(message))

            if 1 <= value <= 10:
                return value

            print("Score must be between 1 and 10.")

        except ValueError:
            print("Please enter a valid numerical score.")


def get_criterion_type():
    """Get the criterion type."""
    while True:
        value = input(
            "Type (B = Benefit, C = Cost): "
        ).strip().upper()

        if value in ("B", "C"):
            return value

        print("Please enter B or C.")


# ============================================================
#                    INPUT COLLECTION
# ============================================================

def get_options():
    """Collect the alternatives being compared."""
    print_header("DECISION ALTERNATIVES")

    count = get_integer("Enter the number of options: ")

    options = []

    for i in range(count):
        name = get_non_empty_text(
            f"Enter the name of option {i + 1}: "
        )

        options.append(name)

    return options


def get_criteria():
    """Collect criteria, weights, and criterion types."""
    print_header("DECISION CRITERIA")

    count = get_integer("Enter the number of criteria: ")

    criteria = []
    total_weight = 0

    print("\nCriterion types:")
    print("B = Benefit: Higher scores are better")
    print("C = Cost: Lower scores are better")

    for i in range(count):
        print(f"\nCriterion {i + 1}")

        name = get_non_empty_text("Criterion name: ")
        weight = get_positive_float("Importance weight: ")
        criterion_type = get_criterion_type()

        criteria.append({
            "name": name,
            "weight": weight,
            "type": criterion_type
        })

        total_weight += weight

    # Normalize weights so their total equals 100%.
    for criterion in criteria:
        criterion["weight"] = (
            criterion["weight"] / total_weight
        ) * 100

    return criteria


def collect_scores(options, criteria):
    """Collect scores for each option against every criterion."""
    print_header("ENTER CRITERION SCORES")

    print("Enter scores between 1 and 10.")
    print("For cost criteria, 1 means low cost and 10 means high cost.")

    scores = {}

    for option in options:
        print(f"\nScores for: {option}")

        scores[option] = {}

        for criterion in criteria:
            name = criterion["name"]

            score = get_score(f"{name}: ")

            scores[option][name] = score

    return scores


# ============================================================
#                    SCORE CALCULATION
# ============================================================

def calculate_option_score(option, criteria, scores):
    """
    Calculate the weighted score.

    Benefit: use the original score.
    Cost: convert score using 11 - score.

    Maximum possible total score = 10.
    """
    total = 0

    for criterion in criteria:
        name = criterion["name"]
        weight = criterion["weight"]
        criterion_type = criterion["type"]

        original_score = scores[option][name]

        if criterion_type == "C":
            adjusted_score = 11 - original_score
        else:
            adjusted_score = original_score

        contribution = adjusted_score * weight / 100

        total += contribution

    return total


def calculate_all_scores(options, criteria, scores):
    """Calculate the final score of every option."""
    results = {}

    for option in options:
        results[option] = calculate_option_score(
            option, criteria, scores
        )

    return results


def rank_options(results):
    """Sort options by score in descending order."""
    return sorted(
        results.items(),
        key=lambda item: item[1],
        reverse=True
    )


# ============================================================
#                    DISPLAY FUNCTIONS
# ============================================================

def display_criteria(criteria):
    """Display normalized criteria weights."""
    print_header("CRITERIA WEIGHT SUMMARY")

    print(f"{'Criterion':<30}{'Weight (%)':>15}{'Type':>20}")
    print("-" * 65)

    for criterion in criteria:
        criterion_type = (
            "Benefit"
            if criterion["type"] == "B"
            else "Cost"
        )

        print(
            f"{criterion['name']:<30}"
            f"{criterion['weight']:>14.2f}%"
            f"{criterion_type:>20}"
        )

    print("-" * 65)

    print(
        f"{'TOTAL':<30}"
        f"{sum(c['weight'] for c in criteria):>14.2f}%"
    )


def display_ranking(ranked_results):
    """Display the final ranking."""
    print_header("FINAL DECISION RANKING")

    print(
        f"{'Rank':<10}"
        f"{'Option':<30}"
        f"{'Score / 10':>15}"
        f"{'Performance':>18}"
    )

    print("-" * WIDTH)

    for rank, (option, score) in enumerate(
        ranked_results, start=1
    ):
        percentage = score * 10

        print(
            f"{rank:<10}"
            f"{option:<30}"
            f"{score:>15.2f}"
            f"{percentage:>17.2f}%"
        )


def display_comparison(ranked_results):
    """Display a text-based bar chart of option scores."""
    print_header("VISUAL SCORE COMPARISON")

    for option, score in ranked_results:
        bar_length = round(score * 5)

        bar = "#" * bar_length

        print(
            f"{option[:22]:<23} | "
            f"{bar:<50} {score:.2f}/10"
        )


def display_score_breakdown(
    option, criteria, scores
):
    """Display the weighted contribution of each criterion."""
    print_header(f"SCORE BREAKDOWN: {option}")

    print(
        f"{'Criterion':<25}"
        f"{'Raw Score':>12}"
        f"{'Weight':>12}"
        f"{'Adjusted':>12}"
        f"{'Contribution':>17}"
    )

    print("-" * WIDTH)

    total = 0

    for criterion in criteria:
        name = criterion["name"]
        weight = criterion["weight"]
        criterion_type = criterion["type"]

        raw_score = scores[option][name]

        adjusted_score = (
            11 - raw_score
            if criterion_type == "C"
            else raw_score
        )

        contribution = adjusted_score * weight / 100
        total += contribution

        print(
            f"{name[:24]:<25}"
            f"{raw_score:>12.2f}"
            f"{weight:>11.2f}%"
            f"{adjusted_score:>12.2f}"
            f"{contribution:>17.2f}"
        )

    print("-" * WIDTH)
    print(f"{'TOTAL WEIGHTED SCORE':<60}{total:>10.2f}")


def display_recommendation(ranked_results):
    """Display the recommended option and handle ties."""
    print_header("FINAL RECOMMENDATION")

    best_score = ranked_results[0][1]

    # Treat scores within this tolerance as tied.
    tolerance = 0.0001

    winners = [
        option
        for option, score in ranked_results
        if abs(score - best_score) < tolerance
    ]

    if len(winners) == 1:
        print(f"Recommended option : {winners[0]}")
    else:
        print("Multiple options share the highest score:")

        for winner in winners:
            print(f"  - {winner}")

    print(f"Highest score      : {best_score:.2f}/10")
    print(f"Performance        : {best_score * 10:.2f}%")

    print(
        "\nRecommendation is based on the criteria, "
        "weights, and scores entered by the user."
    )


# ============================================================
#                       CSV EXPORT
# ============================================================

def export_results(
    criteria, ranked_results, scores
):
    """Export ranking and criterion scores to a CSV file."""
    print_header("EXPORT RESULTS")

    choice = input(
        "Do you want to export results to CSV? (Y/N): "
    ).strip().upper()

    if choice != "Y":
        print("CSV export skipped.")
        return

    filename = (
        "decision_results_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".csv"
    )

    try:
        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Rank",
                "Option",
                "Final Score",
                "Performance (%)"
            ] + [
                criterion["name"]
                for criterion in criteria
            ])

            for rank, (option, score) in enumerate(
                ranked_results, start=1
            ):
                writer.writerow([
                    rank,
                    option,
                    round(score, 2),
                    round(score * 10, 2)
                ] + [
                    scores[option][criterion["name"]]
                    for criterion in criteria
                ])

        print(f"Results exported successfully to {filename}")

    except OSError as error:
        print(f"Unable to export results: {error}")


# ============================================================
#                       MAIN PROGRAM
# ============================================================

def main():
    print_header("DECISION OPTIMIZATION TOOL")

    print("Make better decisions using weighted criteria.")
    print("Supports benefit criteria, cost criteria, and ranking.")

    # Step 1: Collect inputs.
    options = get_options()
    criteria = get_criteria()
    scores = collect_scores(options, criteria)

    # Step 2: Calculate scores.
    results = calculate_all_scores(
        options, criteria, scores
    )

    # Step 3: Rank the alternatives.
    ranked_results = rank_options(results)

    # Step 4: Display results.
    display_criteria(criteria)
    display_ranking(ranked_results)
    display_comparison(ranked_results)
    display_recommendation(ranked_results)

    # Step 5: Display breakdown for every option.
    print_header("DETAILED SCORE BREAKDOWN")

    for option, score in ranked_results:
        display_score_breakdown(
            option, criteria, scores
        )

    # Step 6: Export results if requested.
    export_results(criteria, ranked_results, scores)

    print_header("DECISION PROCESS COMPLETED")


if __name__ == "__main__":
    main()

