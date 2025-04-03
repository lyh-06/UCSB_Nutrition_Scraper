from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import argparse

def calculate_nutrient_density(nutrients):
    """
    Calculate nutrient density

    Arg: Dictionary of nutrient values
    Return: Float of nutrient value (higher = better)
    """
    if 'Calories' not in nutrients or nutrients['Calories'] == 0:
        return 0

    calories = nutrients['Calories']
    score = 0

    # Positive nutrients (higher = better)
    protein = nutrients.get('Protein (g)', 0)
    fiber = nutrients.get('Dietary Fiber (g)', 0)
    iron = nutrients.get('Iron (mg)', 0)
    calcium = nutrients.get('Calcium (mg)', 0)
    vitamin_a = nutrients.get('Vitamin A (µg)', 0)
    vitamin_c = nutrients.get('Vitamin C (µg)', 0)

    # Calculate score components, (per calorie, weighted by importance)
    score += (protein/calories) * 3.0
    score += (fiber/calories) * 2.0
    score += (iron/calories) * 1.5
    score += (calcium/calories) * 1.0
    score += (vitamin_a/calories) * 1.0
    score += (vitamin_c/calories) * 1.0

    # Negative nutrients (higher = worse)
    saturated_fat = nutrients.get('Saturated Fat (g)', 0)
    sodium = nutrients.get('Sodium (mg)', 0)

    # Calculate score components, (per calorie, weighted by importance)
    score -= (saturated_fat/calories) * 1.5
    score -= (sodium/calories) * 1.0

    return score * 100

def extract_numerical_value(text):
    """
    Extract numerical value from string
    e.g extract 12 from '12g'
    """
    if not text:
        return 0
    
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    else:
        return 0

def reset_navigation(browser, dining_common_id):
    """Reset navigation to dining commons menu page"""
    # Go back to main page
    browser.get("https://nutrition.info.dining.ucsb.edu/NetNutrition/1")
    time.sleep(3)
    
    # Select dining common
    browser.execute_script(f"NetNutrition.UI.unitsSelectUnit({dining_common_id});")
    time.sleep(3)
    
    # Select Daily Menu
    menu_id = dining_common_id + 1
    browser.execute_script(f"NetNutrition.UI.childUnitsSelectUnit({menu_id});")
    time.sleep(3)
    
    return browser.find_elements(By.CSS_SELECTOR, ".cbo_nn_menuLink")

def scrape_most_nutrient_dense_foods(dining_common_id, meal_filter=None, num_foods=10, max_categories=3, max_items_per_category=15, start_category = 0):
    """
    Find the most nutrient dense foods at a UCSB dining common
    """
    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    # Initialize WebDriver
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(browser, 10)

    all_foods = []
    dining_common_name = ""

    try:
        # Step 1: Open NetNutrition website
        print("Opening UCSB NetNutrition website")
        browser.get("https://nutrition.info.dining.ucsb.edu/NetNutrition/1")
        time.sleep(3)

        # Step 2: Select dining common
        print(f"Selecting dining common with ID: {dining_common_id}")
        browser.execute_script(f"NetNutrition.UI.unitsSelectUnit({dining_common_id});")
        time.sleep(3)

        # Get dining common name
        header = browser.find_element(By.ID, "cbo_nn_HeaderSelectedUnit")
        dining_common_name = header.text
        print(f"Dining Common: {dining_common_name}")

        # Step 3: Select "Daily Menu"
        menu_id = dining_common_id + 1
        print("Selecting Daily Menu")
        browser.execute_script(f"NetNutrition.UI.childUnitsSelectUnit({menu_id});")
        time.sleep(3)

        # Step 4: Get all menu categories
        categories = browser.find_elements(By.CSS_SELECTOR, ".cbo_nn_menuLink")
        category_count = len(categories)
        print(f"Found {category_count} menu categories")
        
        # Process each category
        end_category = min(start_category + max_categories, category_count)
        categories_to_process = []

        if meal_filter and meal_filter != 'all':
            # Filter categories by meal type
            for i in range(start_category, end_category):
                if i < len(categories) and meal_filter.lower() in categories[i].text.lower():
                    categories_to_process.append(i)

            if not categories_to_process:
                print(f"No {meal_filter} meal found for the selected day")
        else:
            # Process all meals for the selected day
            categories_to_process = list(range(start_category, end_category))

        for category_index in categories_to_process:
            print(f"\nProcessing category {category_index+1}/{len(categories_to_process)}")
            
            # Reset navigation for each category to avoid stale elements
            categories = reset_navigation(browser, dining_common_id)
            
            if category_index >= len(categories):
                print(f"Category index {category_index} no longer available, skipping")
                continue
                
            category = categories[category_index]
            category_name = category.text
            print(f"Category: {category_name}")
            
            # Click category
            browser.execute_script("arguments[0].click();", category)
            time.sleep(3)
            
            # Get food items
            items = browser.find_elements(By.CSS_SELECTOR, ".cbo_nn_itemHover")
            item_count = len(items)
            
            if item_count == 0:
                print("No food items found in this category")
                continue
                
            print(f"Found {item_count} food items")
            
            # Process each food item
            for item_index in range(item_count):
                # Reset to category page for each new item
                if item_index > 0:
                    # Reset to category
                    categories = reset_navigation(browser, dining_common_id)
                    # Click on category again
                    browser.execute_script("arguments[0].click();", categories[category_index])
                    time.sleep(3)
                    # Get fresh items
                    items = browser.find_elements(By.CSS_SELECTOR, ".cbo_nn_itemHover")
                    if item_index >= len(items):
                        print(f"Item index {item_index} no longer available, skipping")
                        continue
                
                item = browser.find_elements(By.CSS_SELECTOR, ".cbo_nn_itemHover")[item_index]
                item_name = item.text
                print(f"\tProcessing item {item_index+1}/{item_count}: {item_name}")
                
                # Click on food item
                browser.execute_script("arguments[0].click();", item)
                time.sleep(3)
                
                # Extract nutrition info
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                nutrition_label = soup.find(id="nutritionLabel")
                
                if nutrition_label:
                    # Create dictionary for nutrient values
                    nutrients = {
                        'name': item_name,
                        'category': category_name
                    }
                    
                    # Get calories
                    calories_element = nutrition_label.find("div", class_="font-22")
                    if calories_element:
                        nutrients['Calories'] = extract_numerical_value(calories_element.text)
                    
                    # Get nutrient rows - more reliable way to find all nutrients
                    all_rows = nutrition_label.find_all("div", class_="cbo_nn_LabelBorderedSubHeader")
                    
                    # Process each nutrient row
                    for row in all_rows:
                        # Extract nutrient name and value
                        spans = row.find_all("span")
                        if len(spans) >= 2:
                            nutrient_name = spans[0].text.strip()
                            value_text = spans[1].text.strip()
                            
                            # Store in nutrients dictionary with proper key
                            if 'Protein' in nutrient_name:
                                nutrients['Protein (g)'] = extract_numerical_value(value_text)
                            elif 'Dietary Fiber' in nutrient_name:
                                nutrients['Dietary Fiber (g)'] = extract_numerical_value(value_text)
                            elif 'Saturated Fat' in nutrient_name:
                                nutrients['Saturated Fat (g)'] = extract_numerical_value(value_text)
                            elif 'Sodium' in nutrient_name:
                                nutrients['Sodium (mg)'] = extract_numerical_value(value_text)
                            elif 'Iron' in nutrient_name:
                                nutrients['Iron (mg)'] = extract_numerical_value(value_text)
                            elif 'Calcium' in nutrient_name:
                                nutrients['Calcium (mg)'] = extract_numerical_value(value_text)
                            elif 'Vitamin A' in nutrient_name:
                                nutrients['Vitamin A (µg)'] = extract_numerical_value(value_text)
                            elif 'Vitamin C' in nutrient_name:
                                nutrients['Vitamin C (µg)'] = extract_numerical_value(value_text)
                    
                    # Print the extracted nutrients for debugging
                    print(f"\t\tCalories: {nutrients.get('Calories')}")
                    print(f"\t\tProtein: {nutrients.get('Protein (g)')}g")
                    print(f"\t\tFiber: {nutrients.get('Dietary Fiber (g)')}g")
                    
                    # Calculate and store nutrient density score
                    nutrients['nutrient_density_score'] = calculate_nutrient_density(nutrients)
                    
                    # Add to foods list
                    all_foods.append(nutrients)
        
        # Create DataFrame and sort by nutrient density
        if all_foods:
            df = pd.DataFrame(all_foods)
            df = df.sort_values('nutrient_density_score', ascending=False)
            return dining_common_name, df.head(num_foods)
        else:
            print("No food items found")
            return dining_common_name, pd.DataFrame()
    
    except Exception as e:
        print(f"Error: {e}")
        return dining_common_name, pd.DataFrame()
    finally:
        browser.quit()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Scrape most nutrient-dense foods at UCSB dining commons')
    parser.add_argument('--dining-common', type=str, choices=['carrillo', 'dlg', 'ortega', 'portola'], default='dlg', help='Dining common to scrape')
    parser.add_argument('--meal', type=str, choices=['breakfast', 'lunch', 'dinner', 'brunch', 'all'], 
                    default='all', help='Which meal to process (breakfast, lunch, dinner, brunch, or all)')
    parser.add_argument('--top', type=int, default=10, help='Number of top foods to display')
    parser.add_argument('--output', type=str, help='Output CSV File (optional)')
    parser.add_argument('--day', type=int, default=1, help='Which day to process (1-7, default is today/Day 1)')
    parser.add_argument('--max-items', type=int, default=15, help='Maximum number of items per category to process')

    args = parser.parse_args()

    # Map dining common names to IDs
    dining_common_ids = {
        'carrillo': 9,
        'dlg': 3,
        'ortega': 16,
        'portola': 15
    }

    dining_id = dining_common_ids[args.dining_common]

    max_categories = 3
    start_category = (args.day - 1) *3


    # Find most nutrient-dense foods
    dining_name, top_foods = scrape_most_nutrient_dense_foods(dining_id, args.meal, args.top, max_categories, args.max_items, start_category=start_category)

    if not top_foods.empty:
        print(f"\n==== Top {args.top} Most Nutrient-Dense Foods at {dining_name} =====\n")

        # Display formatted results
        for i, (_, food) in enumerate(top_foods.iterrows(), 1):
            print(f"{i}. {food['name']}")
            print(f"\tNutrient density score: {food['nutrient_density_score']:.2f}")
            print(f"\tCategory: {food['category']}")
            print(f"\tCalories: {food.get('Calories', 'N/A')}")
            print(f"\tProtein: {food.get('Protein (g)', 'N/A')}g")
            print(f"\tFiber: {food.get('Dietary Fiber (g)','N/A')}g")
        
        # Save to CSV if requested
        if args.output:
            top_foods.to_csv(args.output, index=False)
            print(f"Results saved to {args.output}")
    else:
        print(f"No results found for {dining_name}")

if __name__ == "__main__":
    main()