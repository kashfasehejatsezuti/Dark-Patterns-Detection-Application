from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from model_training.scraping import delete_files_in_scraped_data
import dark_pattern_service

dark_pattern = Blueprint('dark_pattern', __name__, url_prefix='/darkPattern')


@dark_pattern.route('/createModel', methods=['GET'])
@cross_origin()
def create_dark_pattern_model():
    return dark_pattern_service.create_model()


@dark_pattern.route('/<string:website_id>', methods=['POST'])
@cross_origin()
def parse_website_for_dark_pattern_detection(website_id):
    return dark_pattern_service.parse_website_url(website_id, params=request.json)


@dark_pattern.route('/freeCheck', methods=['GET'])
@cross_origin()
def free_verification():
    delete_files_in_scraped_data()
    website_url = request.args.get('url')
    return dark_pattern_service.free_verification(params={'url': website_url})

@dark_pattern.route('/webpageList', methods=['POST'])
@cross_origin()
def parse_multiple_website_for_dark_pattern_detection():
    delete_files_in_scraped_data()
    data = request.json
    
    for i, j in data.items():
        webpageList= j

    response = dark_pattern_service.parse_multiple_website_url(webpageList)
    return jsonify(response)

   