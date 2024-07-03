import inquirer

def run_setup_inquiry():
    # Ask the user what style they'd like to generate
    run_options = [
        inquirer.List(
            "style",
            message="What style of background would you like to generate?",
            choices=[
                "Space",
                "Japan",
                "Location-Based",
                "Abstract",
                "Mixed",
            ],
        ),
        inquirer.List(
            "cadence",
            message="How often would you like it to change?",
            choices=[
                "Daily",
                "Every 8 hours",
                "Every 4 hours",
                "Every 2 hours",
                "Hourly",
                "Every 30 minutes",
                "Every 15 minutes",
                "Every 5 minutes",
                "Every minute",
            ],
        ),
    ]

    inquiry_answers = inquirer.prompt(run_options)
    style_choice = inquiry_answers["style"]
    cadence_choice = inquiry_answers["cadence"]

    cadence_choice_map = {
        "Daily": 1440,
        "Every 8 hours": 480,
        "Every 4 hours": 240,
        "Every 2 hours": 120,
        "Hourly": 60,
        "Every 30 minutes": 30,
        "Every 15 minutes": 30,
        "Every 5 minutes": 5,
        "Every minute": 1
    }

    cadence = cadence_choice_map[cadence_choice]

    return (style_choice, cadence)