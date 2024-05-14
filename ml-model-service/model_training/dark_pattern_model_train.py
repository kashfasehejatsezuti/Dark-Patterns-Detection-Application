import os
import csv
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
from joblib import dump, load


def read_and_clean_dataset(file_input_path):
    # Load the CSV file
    df = pd.read_csv(file_input_path)
    print(f"Initial DataFrame count: {len(df)}")
    df.head()

    # Drop rows with missing values in the 'Text' column
    df = df.dropna(subset=['Text'])

    # Ensure 'Text' column has string data type
    df['Text'] = df['Text'].astype(str)

    # Reset the index of the DataFrame
    df = df.reset_index(drop=True)

    return df


def train_and_evaluate_model(df, target_column, save_filename):
    # Split the dataset into training and testing sets
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=34)

    # Create a pipeline for the model
    model = make_pipeline(TfidfVectorizer(), SVC())

    # Fit the model
    model.fit(train_df['Text'], train_df[target_column])

    # Evaluate the model on the test set
    predictions = model.predict(test_df['Text'])
    accuracy = accuracy_score(test_df[target_column], predictions)

    # Save the trained model to a file
    model_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_models")
    os.makedirs(model_folder, exist_ok=True)
    model_path = os.path.join(model_folder, f'{save_filename.lower().replace(" ", "_")}_model.joblib')
    dump(model, model_path)

    # Return the accuracy and the trained model
    return accuracy, model


def train_first_level_model(df, dark_pattern_types):
    print(f"\nTraining first level model")
    # Create a boolean mask for Dark Patterns
    dark_pattern_mask = df['Type'].isin(dark_pattern_types)

    # Assign labels for the first-level model (0 for Not Dark Patterns, 1 for Dark Patterns)
    df['Label'] = dark_pattern_mask.astype(int)

    # Train and evaluate the first-level model using Multinomial Naive Bayes
    accuracy, model = train_and_evaluate_model(df, 'Label', "first_level")
    print(f"First Level Model Accuracy: {accuracy:.2f}")

    # Remove the extra column
    df.drop(columns=['Label'], inplace=True)


def train_second_level_models(df, dark_pattern_types):
    # Filter the original DataFrame to select dataframe containing dark patterns
    dark_patterns_df = df[df['Type'].isin(dark_pattern_types)]

    for dark_pattern_type in dark_pattern_types:
        print(f"\nTraining second level model for: {dark_pattern_type}")

        # Filter the dataset for the specific Dark Pattern type
        positive_df = dark_patterns_df[dark_patterns_df['Type'] == dark_pattern_type].copy()

        # Create a combined negative dataset
        negative_df = dark_patterns_df[dark_patterns_df['Type'] != dark_pattern_type].copy()

        # Ensure that negative_df contains instances with Label as 0 and positive_df with Label as 1
        positive_df.loc[:, 'Label'] = 1
        negative_df.loc[:, 'Label'] = 0

        # Ensure that the negative dataset has the same number of instances as the positive dataset
        negative_df = negative_df.sample(n=len(positive_df), random_state=43)

        # Combine positive and negative datasets
        train_combined_df = pd.concat([positive_df, negative_df]).sample(frac=1, random_state=34).reset_index(drop=True)

        # Train and evaluate the second-level model using Multinomial Naive Bayes
        accuracy, model = train_and_evaluate_model(train_combined_df, 'Label', dark_pattern_type)
        print(f"{dark_pattern_type} Model Accuracy: {accuracy:.2f}")

        # Remove the extra column
        train_combined_df.drop(columns=['Label'], inplace=True)


def predict_dark_pattern(input_text):

    dark_pattern_types = ["Scarcity", "Social Proof", "Urgency"]

    # Load and make predictions with the first-level model
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    first_level_model_path = os.path.join(current_script_path, "trained_models", "first_level_model.joblib")
    loaded_first_level_model = load(first_level_model_path)

    # Make first level prediction
    first_level_prediction = loaded_first_level_model.predict([input_text])

    # Check if it is identified as a Dark Pattern
    if first_level_prediction[0] == 1:
        # Load and make predictions with the second-level models
        for dark_pattern_type in dark_pattern_types:
            # Load the saved second-level model
            current_script_path = os.path.dirname(os.path.abspath(__file__))
            second_level_model_path = os.path.join(current_script_path, "trained_models",
                                                   f'{dark_pattern_type.lower().replace(" ", "_")}_model.joblib')
            loaded_second_level_model = load(second_level_model_path)

            # Make second level prediction
            second_level_prediction = loaded_second_level_model.predict([input_text])

            if second_level_prediction[0] == 1:
                return dark_pattern_type
    else:
        return "Not Dark Pattern"


def create_dark_pattern_detection_model():
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_file_path, "dataset.csv")
    dark_pattern_types = ["Scarcity", "Social Proof", "Urgency"]

    filtered_df = read_and_clean_dataset(csv_path)
    train_first_level_model(filtered_df, dark_pattern_types)
    train_second_level_models(filtered_df, dark_pattern_types)


def get_csv_file_path(website_id):
    ml_model_directory = os.path.dirname(os.path.abspath(__file__))
    scraped_data_directory = os.path.join(ml_model_directory, "scraped_data")
    csv_file_path = os.path.join(scraped_data_directory, "{}.csv".format(website_id))
    return csv_file_path


def predict_website_dark_pattern_type(website_id):
    csv_file_path = get_csv_file_path(website_id)
    dark_patterns ={}

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:
                    text_to_predict = row[0]
                    detected_type = predict_dark_pattern(text_to_predict)
                    if detected_type is not None and detected_type != "Not Dark Pattern":
                        dark_patterns[text_to_predict] = detected_type
        print(f'Data has been successfully read from {csv_file_path}')
    except FileNotFoundError:
        print(f'File not found: {csv_file_path}')
    except Exception as e:
        print(f'Error reading the file: {e}')

    return dark_patterns
