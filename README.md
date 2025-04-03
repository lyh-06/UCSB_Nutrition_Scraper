## UCSB Dining Nutrient Scraper
A Python script to analyze nutrient density of foods served at the UCSB dining commons. 

## Features
- Scrape real-time nutritional information from https://nutrition.info.dining.ucsb.edu/NetNutrition/1#
- Calculate nutrient density scores based on protein, fiber, vitamins, etc.
- Filter by meal type (breakfast, lunch, dinner, brunch, all)
- Generate top 10 lits with customizable parameters
- Optionally export results to CSV file

## Installation
1. Clone this repository:
git clone https://github.com/yourusername/ucsb-netnutrition-scraper.git
cd ucsb-netnutrition-scraper

2. Create a virtual environment (recommended):
python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install required packages:
pip install -r requirements.txt

## Usage
Basic usage:
python ucsb_netnutrition_scraper.py

Advanced options:
python ucsb_netnutrition_scraper.py --dining-common dlg --meal lunch --top 15 --output results.csv

## Command Line Arguments
--dining-common: Dining common to scrape
[carrillo, dlg, ortega, portola](default: dlg)

--meal: Meal to process [breakfast, lunch, dinner, brunch, all](default: all)

--top: Number of top foods to display(default: 10)

--output: Output CSV file (optional)

--day: Which day to process(1-7, default is 1/today)

--max-items: Maximum items to process per category (default: 15)

## Example Output
==== Top 10 Most Nutrient-Dense Foods at Portola Dining Commons =====

1. Baby Spinach (vgn)
        Nutrient density score: 283.10
        Category: Breakfast
        Calories: 5.0
        Protein: 1.0g
        Fiber: 1.0g
2. Quinoa Breakfast Bowl (w/nuts) (v)
        Nutrient density score: 141.70
        Category: Breakfast
        Calories: 60.0
        Protein: 2.0g
        Fiber: 1.0g
...

## How it Works
The program uses Selenium WebDriver to navigate through the NetNutrition website, which requires JavScript interaction. It goes through these steps:
1. Opens the NetNutrition website
2. Navigates to the selected dining common
3. Goes to the daily menu
4. Processes each meal category
5. Clicks on each food item to retrieve nutritional info
6. Calculate nutritient density score
7. Sorts and displays the most nutrient-dense options

## Nutrient Density Calculation;
The nutrient density score is calculated using the following formula:
score = (
    protein * 3.0 + 
    fiber * 2.0 + 
    iron * 1.5 + 
    calcium * 1.0 + 
    vitamin_a * 1.0 + 
    vitamin_c * 1.0 - 
    saturated_fat * 1.5 - 
    sodium * 1.0
) / calories * 100

Note: The weights of each nutrient can be modified to suit induvidual needs and preferences (ex: athletes can change the score multiplier for protein from 3.0 to 5.0)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License- see the LICENSE file for details.

## Disclaimer
This tool is not affiliated with UCSB Dining services. The nutrient density calcilations are based on a simplified model and should not replace professional dietary advice.