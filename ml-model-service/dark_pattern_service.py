from model_training.dark_pattern_model_train import get_csv_file_path, predict_website_dark_pattern_type, \
    create_dark_pattern_detection_model
from model_training.scraping import web_scrap
from flask import jsonify
import pandas as pd
import random
import string


def create_model():
    print('Creating Dark Pattern Model')
    create_dark_pattern_detection_model()
    return 'Successfully model created', 200


def parse_website_url(website_id, params):
    print('Parsing website')
    website_url = params['websiteUrl']

    web_scrap(website_url, website_id)

    dark_patterns = predict_website_dark_pattern_type(website_id)
    dark_patterns = [{'text': key, 'patternType': value} for key, value in dark_patterns.items()]

    return jsonify(dark_patterns)


def free_verification(params):
    website_url = params['url']
    result = web_scrap(website_url, '65b3de8af380a27e55c21102')

    if result == 'Done':
        csv_file_path = get_csv_file_path('65b3de8af380a27e55c21102')
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                df = pd.read_csv(file)
                rows = len(df.axes[0])
            print(f'Data has been successfully read')
        except FileNotFoundError:
            print(f'File not found: {csv_file_path}')
        except Exception as e:
            print(f'Error reading the file: {e}')

        dark_patterns = predict_website_dark_pattern_type('65b3de8af380a27e55c21102')
        if len(dark_patterns):
            len_dp = rows - len(dark_patterns)
            try:
                percentage = round((len_dp/rows)*100)
                return jsonify({'Percentage': percentage})
            except ZeroDivisionError as div_error:
                error_message = str(div_error)
                return jsonify({"error": error_message}), 400
            except Exception as e:
                error_message = str(e)
                return jsonify({"error": error_message}), 500
        else:
            return jsonify({'Percentage': 100})
        

def parse_multiple_website_url(webpageList):
    i=0
    total_webpages = len(webpageList)
    dark_patterns_response = []

    while i<total_webpages:
        webpage_url = webpageList[i]
        website_id = generate_random_id()
        web_scrap(webpage_url, website_id)
        dark_patterns = predict_website_dark_pattern_type(website_id)
        dark_patterns = [{'webpageUrl': webpage_url, 'text': key, 'patternType': value} for key, value in dark_patterns.items()]
        for obj in dark_patterns:
            dark_patterns_response.append(obj)
        i+=1
    else: 
        return dark_patterns_response

# Code to generate random ID for a webpage to run automation 
def generate_random_id():
    characters = string.ascii_lowercase + string.digits
    random_id = ''.join(random.choices(characters, k=24))
    return random_id

