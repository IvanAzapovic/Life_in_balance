import streamlit as st
from shared import get_exercises_for_muscle, insert_exercises_data

# Set the background image and text color
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZ7RL3tzGaC6fl5QbUPu6ACzoRZC7df7PEBQ&s);
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


st.title("Explore Exercises")

if st.session_state.get('show_nutrition', False):
    muscle_group = st.selectbox('Select a Muscle Group', [
        "abdominals", "abductors", "adductors", "biceps", "calves",
        "chest", "forearms", "glutes", "hamstrings", "lats", 
        "lower_back", "middle_back", "neck", "quadriceps", "traps", "triceps"
    ])
    
    if st.button('Find Exercises'):
        try:
            exercises = get_exercises_for_muscle(muscle_group)

            if exercises:
                # Insert exercise session details into the database
                insert_exercises_data(
                    user_id=st.session_state['user_id'],
                    muscle_group=muscle_group,
                    exercises=exercises
                )    
                st.session_state['exercises'] = exercises

                st.success(f"Exercises for {muscle_group.capitalize()} have been found and logged!")
            else:
                st.warning("No exercises found for the selected muscle group.")
        except Exception as e:
            st.error(f"An error occurred while fetching exercises: {e}")

    if 'exercises' in st.session_state:
        st.subheader(f"Exercises for {muscle_group.capitalize()}")
        for exercise in st.session_state['exercises']:
            st.markdown(f"**Name**: {exercise['name']}")
            st.text(f"Type: {exercise['type']}")
            st.text(f"Equipment: {exercise['equipment']}")
            st.text(f"Difficulty: {exercise['difficulty']}")
            st.markdown(f"**Instructions**: {exercise['instructions']}\n")
            st.markdown("---")
else:
    st.warning("Please calculate your nutritional needs on the Nutrition Recommendations page first.")