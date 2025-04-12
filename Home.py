import streamlit as st
import pandas as pd
from shared import calculate_bmi, register_user, login_user, insert_nutrition_data
from PIL import Image
import base64

# Define the path to your local image
file_path = r"C:\Users\Tijana&Ivan\Desktop\Final Project\Balanced_Life\Pictures\Screenshot 2025-04-10 182902.png"

# Function to encode an image to Base64
def get_base64_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Obtain Base64 string of the image
base64_image = get_base64_image(file_path)

# CSS to set a background with the gradient and the embedded image
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(135deg, rgba(113, 183, 230, 0.5), rgba(155, 89, 182, 0.5)), url(data:image/png;base64,{base64_image});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

if 'user_id' not in st.session_state:
    # Initial title for new users
    st.title("Login or Register")

    # Choice selector for either logging in or registering new users
    choice = st.radio("Choose action", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if choice == "Register":
        # Additional fields for registration
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number (Optional)")

        if st.button("Register"):
            if register_user(username, password, first_name, last_name, email, phone_number):
                st.success("Successfully registered! Please log in.")
            else:
                st.error("Registration failed. Try a different username.")
    elif choice == "Login" and st.button("Login"):
        user_id = login_user(username, password)
        if user_id:
            st.session_state['user_id'] = user_id
            st.success("Logged in successfully!")
        else:
            st.error("Login failed. Check your username and password.")
    st.stop()

# If already logged in, show the main app content
st.title("Balanced Life")
st.subheader("Welcome!")

# Load and display user's initial data
country_averages = pd.read_csv('country_nutrient_averages.csv')
country_list = country_averages['country'].unique()

st.subheader('Nutrition and Exercise Calculator')

country = st.selectbox('Choose your Country', country_list)
age = st.number_input('Age', min_value=16, step=1)
gender = st.radio('Gender', ('Male', 'Female'))
weight = st.number_input('Weight (kg)', min_value=20.0, format="%.1f", step=0.1)
height = st.number_input('Height (m)', min_value=1.0, format="%.2f")
activity_level = st.selectbox('Activity Level', ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extremely Active'])

if st.button('Calculate your BMI'):
    bmi, classification = calculate_bmi(weight, height)
    if bmi is not None:
        st.session_state.update({
            'bmi': bmi,
            'classification': classification,
            'show_bmi': True
        })
        
        # Insert nutrition data instead of updating
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
            basic_calories=None,
            optimal_calories=None,
            protein=None,
            fat=None,
            carbs=None,
            dietary_preference=None
        )

if st.session_state.get('show_bmi', False):
    st.subheader(f"Your BMI: {st.session_state['bmi']:.2f}")
    st.subheader(f"BMI Classification: {st.session_state['classification']}")
    st.image(
        'https://qph.cf2.quoracdn.net/main-qimg-27ac647c65b40ca4b5afe4fec523565f-lq', 
        caption="BMI Categories"
    )

    # Update session state with current inputs
    st.session_state.update({
        'country': country,
        'age': age,
        'gender': gender,
        'weight': weight,
        'height': height,
        'activity_level': activity_level
    })

# Save user data or proceed to other module operations
else:
    st.warning("Please make sure to complete the registration and login processes before proceeding with the app.")
