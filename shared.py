import bcrypt
import mysql.connector
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('sql_pass'),
            database='balanced_life'
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def register_user(username, password, first_name, last_name, email, phone_number=None):
    connection = get_db_connection()
    if connection:
        try:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            query = """
            INSERT INTO users (username, password_hash, first_name, last_name, email, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (username, password_hash.decode('utf-8'), first_name, last_name, email, phone_number)
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"Error registering user: {err}")
            return False
        finally:
            connection.close()
    return False

def login_user(username, password):
    connection = get_db_connection()
    if connection:
        try:
            query = "SELECT id, password_hash FROM users WHERE username = %s"
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()

            if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode('utf-8')):
                return user['id']
            else:
                return None
        except mysql.connector.Error as err:
            print(f"Error during login: {err}")
            return None
        finally:
            connection.close()

def insert_nutrition_data(
    user_id, country, age, gender, weight, height, activity_level,
    bmi, classification, basic_calories, optimal_calories,
    protein, fat, carbs, dietary_preference):

    connection = get_db_connection()
    if connection:
        try:
            query = """
            INSERT INTO user_nutrition_data (
                user_id, country, age, gender, weight_kg, height_m,
                activity_level, bmi, classification, basic_calories,
                optimal_calories, protein_grams, fat_grams, carb_grams, dietary_preference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (
                user_id, country, age, gender, weight, height, activity_level, bmi,
                classification, basic_calories, optimal_calories, protein, 
                fat, carbs, dietary_preference
            )
            cursor = connection.cursor()
            cursor.execute(query, data)
            connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error inserting nutrition data: {err}")
        finally:
            connection.close()

def insert_exercises_data(user_id, muscle_group, exercises):
    connection = get_db_connection()
    if connection:
        try:
            query = """
            INSERT INTO user_exercises_data (
                user_id, muscle_group, exercises
            ) VALUES (%s, %s, %s)
            """
            cursor = connection.cursor()
            cursor.execute(query, (user_id, muscle_group, json.dumps(exercises)))
            connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error inserting exercises data: {err}")
        finally:
            connection.close()

def calculate_bmi(weight, height):
    if height <= 0:
        return None, None
    bmi = weight / (height ** 2)
    classification = (
        "Underweight" if bmi < 18.5 else
        "Healthy Weight" if bmi < 24.9 else
        "Overweight" if bmi < 29.9 else
        "Obesity" if bmi < 34.9 else
        "Severe Obesity"
    )
    return bmi, classification

def calculate_basic_calories(weight_kg, height_cm, age, gender):
    if gender.lower() == 'male':
        return 66.5 + 13.8 * weight_kg + 5.0 * height_cm - 6.8 * age
    else:
        return 655.1 + 9.6 * weight_kg + 1.9 * height_cm - 4.7 * age

def calculate_optimal_calories(basic_calories, activity_level):
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Extremely Active': 1.9
    }
    return basic_calories * activity_multipliers.get(activity_level, 1.2)

def calculate_macronutrients(tdee, weight_kg, activity_level):
    protein_multipliers = {
        'Sedentary': 0.8,
        'Lightly Active': 1.0,
        'Moderately Active': 1.2,
        'Very Active': 1.5,
        'Extremely Active': 1.8
    }
    protein_grams = weight_kg * protein_multipliers[activity_level]
    fat_grams = tdee * 0.3 / 9
    carb_calories = tdee - (protein_grams * 4 + fat_grams * 9)
    carb_grams = carb_calories / 4
    return protein_grams, fat_grams, carb_grams

def get_exercises_for_muscle(muscle):
    api_key = os.getenv('NINJA_API_KEY')
    url = f'https://api.api-ninjas.com/v1/exercises?muscle={muscle}'
    headers = {'X-Api-Key': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch exercises (Status Code: {response.status_code})")
        return []