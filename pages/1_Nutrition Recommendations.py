import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shared import calculate_basic_calories, calculate_optimal_calories, calculate_macronutrients, insert_nutrition_data

# Set the background image and text color
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhu7qO-roSEDZDKMZ0czUX6XzUQ8wuvIyzfQ&s);
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .stMarkdown, .stButton, .stRadio {{
        color: black;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Load data
country_averages = pd.read_csv('country_nutrient_averages.csv')

st.title("Your Nutrition Recommendations")

# Ensure that BMI calculation exists
if st.session_state.get('show_bmi', False):
    weight = st.session_state['weight']
    height = st.session_state['height']
    age = st.session_state['age']
    gender = st.session_state['gender']
    activity_level = st.session_state['activity_level']
    country = st.session_state['country']

    if st.button('Calculate Nutritional Needs'):
        basic_calories = calculate_basic_calories(weight, height * 100, age, gender)
        optimal_calories = calculate_optimal_calories(basic_calories, activity_level)
        protein, fat, carbs = calculate_macronutrients(optimal_calories, weight, activity_level)

        st.session_state.update({
            "is_calculated": True,
            "basic_calories": basic_calories,
            "optimal_calories": optimal_calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs,
            "show_nutrition": True
        })

        # Insert nutrition data into the database
        insert_nutrition_data(
            user_id=st.session_state['user_id'],
            country=country,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            activity_level=activity_level,
            bmi=st.session_state['bmi'],
            classification=st.session_state['classification'],
            basic_calories=basic_calories,
            optimal_calories=optimal_calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            dietary_preference=None
        )

    if st.session_state.get('show_nutrition', False):
        st.subheader("Your Nutrition Needs:")
        st.write(f"- **Daily Energy Use:** {st.session_state['optimal_calories']:.2f} calories")
        st.write(f"- **Protein:** {st.session_state['protein']:.2f} grams")
        st.write(f"- **Fat:** {st.session_state['fat']:.2f} grams")
        st.write(f"- **Carbohydrates:** {st.session_state['carbs']:.2f} grams")

        selected_country_info = country_averages[country_averages['country'] == country].iloc[0]
        st.subheader(f"Average Nutritional Values in {country}:")
        st.write(f"- **Calories:** {selected_country_info['daily_calories_supply']:.2f} calories")
        st.write(f"- **Protein:** {selected_country_info['daily_protein_supply(grams)']:.2f} grams")
        st.write(f"- **Fat:** {selected_country_info['daily_fat_supply(grams)']:.2f} grams")

        user_values = np.array([
            st.session_state['optimal_calories'],
            st.session_state['protein'],
            st.session_state['fat']
        ])
        distances = np.sqrt(
            ((country_averages[[
                'daily_calories_supply', 
                'daily_protein_supply(grams)', 
                'daily_fat_supply(grams)'
            ]] - user_values) ** 2).sum(axis=1)
        )
        closest_country_index = distances.idxmin()
        closest_country = country_averages.loc[closest_country_index, 'country']

        st.subheader(f"Interesting Fact: Your nutritional values align more closely with {closest_country}:")
        st.write(f"- **Average Calories Supply:** {country_averages.loc[closest_country_index, 'daily_calories_supply']:.2f} calories")
        st.write(f"- **Average Protein Supply:** {country_averages.loc[closest_country_index, 'daily_protein_supply(grams)']:.2f} grams")
        st.write(f"- **Average Fat Supply:** {country_averages.loc[closest_country_index, 'daily_fat_supply(grams)']:.2f} grams")

        # Plot all three sets of values
        categories = ['Calories', 'Protein', 'Fat']
        country_values = [
            selected_country_info['daily_calories_supply'], 
                        selected_country_info['daily_protein_supply(grams)'], 
            selected_country_info['daily_fat_supply(grams)']
        ]
        closest_values = [
            country_averages.loc[closest_country_index, 'daily_calories_supply'], 
            country_averages.loc[closest_country_index, 'daily_protein_supply(grams)'], 
            country_averages.loc[closest_country_index, 'daily_fat_supply(grams)']
        ]
        user_values = [
            st.session_state['optimal_calories'],
            st.session_state['protein'],
            st.session_state['fat']
        ]

        # Create a grouped bar chart
        x = np.arange(len(categories))
        width = 0.25  # the width of the bars

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot each set of values
        ax.bar(x - width, country_values, width=width, label=f"Average in {country}", color='b')
        ax.bar(x, closest_values, width=width, label=f"Average in {closest_country}", color='g')
        ax.bar(x + width, user_values, width=width, label='Your Needs', color='r')

        # Chart labeling
        ax.set_ylabel('Values')
        ax.set_title('Nutritional Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()

        # Render the plot in Streamlit
        st.pyplot(fig)

else:
    st.warning("Please calculate your BMI on the home page first to get your nutrition recommendations.")