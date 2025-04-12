import streamlit as st
import pandas as pd
from shared import insert_nutrition_data

# Set the background image and text color
# Set the background image and text color
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRKG9YqNXNxUbdrNuCtU2uce7gBJzQsc9QPRw&s);
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

# Load meals macros from CSV
meals_macros_df = pd.read_csv('meals_macros.csv')

st.title("Dietary Preferences and Meal Plans")

if st.session_state.get('show_nutrition', False):
    # Retrieve user data from session state
    country = st.session_state['country']
    age = st.session_state['age']
    gender = st.session_state['gender']
    weight = st.session_state['weight']
    height = st.session_state['height']
    activity_level = st.session_state['activity_level']
    bmi = st.session_state['bmi']
    classification = st.session_state['classification']
    basic_calories = st.session_state['basic_calories']
    optimal_calories = st.session_state['optimal_calories']
    protein = st.session_state['protein']
    fat = st.session_state['fat']
    carbs = st.session_state['carbs']

    # User selects dietary preference
    dietary_preference = st.selectbox('Select Your Dietary Preference', ['Omnivore', 'Vegan', 'Vegetarian', 'Pescatarian'])
    
    if dietary_preference:
        # Insert user data with updated dietary preference
        insert_nutrition_data(
            user_id=st.session_state['user_id'],
            country=country,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            activity_level=activity_level,
            bmi=bmi,
            classification=classification,
            basic_calories=basic_calories,
            optimal_calories=optimal_calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            dietary_preference=dietary_preference
        )

        # Save dietary preference to session state
        st.session_state['dietary_preference'] = dietary_preference

        # Filter the meals macros based on selected dietary preference
        filtered_meals = meals_macros_df[meals_macros_df['Dietary Preference'] == dietary_preference]

        if not filtered_meals.empty:
            # Calculate the meal plan closest to the user's optimal calorie requirements
            filtered_meals['calorie_diff'] = (filtered_meals['Daily Calorie Target'] - optimal_calories).abs()
            closest_meal_plan_index = filtered_meals['calorie_diff'].idxmin()
            closest_meal_plan = filtered_meals.loc[closest_meal_plan_index]

            # Display the suggested meal plan
            st.subheader("Suggested Meal Plan:")
            st.markdown(f"**Breakfast:** {closest_meal_plan['Breakfast Suggestion']} - Calories: {closest_meal_plan['Breakfast Calories']} Protein: {closest_meal_plan['Breakfast Protein']}g, Carbs: {closest_meal_plan['Breakfast Carbohydrates']}g, Fat: {closest_meal_plan['Breakfast Fats']}g")
            st.markdown(f"**Lunch:** {closest_meal_plan['Lunch Suggestion']} - Calories: {closest_meal_plan['Lunch Calories']} Protein: {closest_meal_plan['Lunch Protein']}g, Carbs: {closest_meal_plan['Lunch Carbohydrates']}g, Fat: {closest_meal_plan['Lunch Fats']}g")
            st.markdown(f"**Dinner:** {closest_meal_plan['Dinner Suggestion']} - Calories: {closest_meal_plan['Dinner Calories']} Protein: {closest_meal_plan['Dinner Protein.1']}g, Carbs: {closest_meal_plan['Dinner Carbohydrates.1']}g, Fat: {closest_meal_plan['Dinner Fats']}g")

            if 'Snack Suggestion' in closest_meal_plan:
                st.markdown(f"**Snacks:** {closest_meal_plan['Snack Suggestion']} - Calories: {closest_meal_plan['Snacks Calories']} Protein: {closest_meal_plan['Snacks Protein']}g, Carbs: {closest_meal_plan['Snacks Carbohydrates']}g, Fat: {closest_meal_plan['Snacks Fats']}g")
else:
    st.warning("Please calculate your nutritional needs on the Nutrition Recommendations page first.")