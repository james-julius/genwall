import inquirer

def run_setup_inquiry():
    # Ask the user what style they'd like to generate
    style_inquiry = [
        inquirer.List(
            "style",
            message="What style of background would you like to generate?",
            choices=[
                "Custom",
                "Space",
                "Random Country",
                "Japan",
                "Location-Based",
                "Abstract",
                "Mixed",
            ],
        ),
    ]

    style_inquiry = inquirer.prompt(style_inquiry)
    style_choice = style_inquiry["style"]
    custom_style_inquiry = None
    custom_style_choice = None

    if style_inquiry["style"] == "Custom":
        custom_style_inquiry = inquirer.prompt([
            inquirer.Text(
                "custom_style",
                message="Please enter a custom background style to generate"
            )
        ])
        custom_style_choice = custom_style_inquiry["custom_style"]


    cadence_inquiry = inquirer.prompt([
        inquirer.List(
            "cadence",
            message="How often would you like it to change?",
            choices=[
                "Every minute",
                "Every 5 minutes",
                "Every 15 minutes",
                "Every 30 minutes",
                "Hourly",
                "Every 2 hours",
                "Every 4 hours",
                "Every 8 hours",
                "Daily",
            ],
        ),
    ])

    cadence_choice = cadence_inquiry["cadence"]

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

    return (style_choice, custom_style_choice, cadence)