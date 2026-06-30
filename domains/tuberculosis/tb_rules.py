TB_RULES = [

    {
        "experiment": "hypoxia",
        "metric": "Dormant%",
        "direction": "increase",
        "message": "Hypoxia should increase dormancy."
    },

    {
        "experiment": "hypoxia",
        "metric": "AverageGrowth",
        "direction": "decrease",
        "message": "Hypoxia should suppress growth."
    },

    {
        "experiment": "hypoxia",
        "metric": "AverageATP",
        "direction": "decrease",
        "message": "Hypoxia should reduce ATP."
    },

    {
        "experiment": "hypoxia",
        "metric": "AverageDosR",
        "direction": "increase",
        "message": "Hypoxia should activate DosR."
    },

    {
        "experiment": "hyperoxia",
        "metric": "AverageGrowth",
        "direction": "increase",
        "message": "Hyperoxia should promote growth."
    },

    {
        "experiment": "treatment",
        "metric": "Population",
        "direction": "decrease",
        "message": "Treatment should reduce bacterial population."
    },

    {
        "experiment": "immune_high",
        "metric": "Stress%",
        "direction": "increase",
        "message": "Strong immune response should increase stress."
    }

]