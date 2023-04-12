import pandas as pd
import pickle
import random

def load_model():
    # load model
    with open('./model/random_forest_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    return rf_model

def get_prediction(user_inputs):

    default_col=[ 'review_duration', 'review_time', 
             'availability_30', 'availability_60', 
             'availability_90', 'availability_365',
             'reviews_per_month', 'review_scores_rating', 
             'review_scores_location','host_response_rate', 
             'host_acceptance_rate', 'number_of_reviews',
             'host_total_listings_count','host_listings_count']
    
    ranges = {
        'review_duration': (1, 365),
        'review_time': (1, 365),
        'availability_30': (0, 30),
        'availability_60': (0, 60),
        'availability_90': (0, 90),
        'availability_365': (0, 365),
        'reviews_per_month': (0, 300),
        'review_scores_rating': (80, 100),
        'review_scores_location': (8, 10),
        'host_response_rate': (8, 10),
        'host_acceptance_rate': (80, 1001),
        'host_listings_count': 44,
        'host_total_listings_count':44,
        'number_of_reviews': 24
    }

    ranges = {
    'review_duration': (1, 365),
    'review_time': (1, 365),
    'availability_30': (0, 30),
    'availability_60': (0, 60),
    'availability_90': (0, 90),
    'availability_365': (0, 365),
    'reviews_per_month': (0, 300),
    'review_scores_rating': (80, 100),
    'review_scores_location': (8, 10),
    'host_response_rate': (8, 10),
    'host_acceptance_rate': (80, 100),
    'number_of_reviews': (0, 1000),
    'host_total_listings_count': (0, 1000),
    'host_listings_count': (0, 10)}

    random_values = {}
    
    for col in default_col:
        random_values[col] = random.randint(ranges[col][0], ranges[col][1])

    df2 = pd.DataFrame([random_values], columns=default_col)
    
    # convert dict to dataframe
    df = pd.DataFrame(user_inputs, index=[0])
    # conver datatype to int
    df = df.astype('int')
    df = pd.concat([df, df2], axis=1)

    order_cols = ['host_response_rate','host_acceptance_rate',
    'host_listings_count','host_total_listings_count',
    'accommodates','bathrooms','bedrooms',
    'beds','minimum_nights',
    'availability_30','availability_60',
    'availability_90','availability_365',
    'number_of_reviews','reviews_per_month',
    'review_duration','review_time',
    'review_scores_rating','review_scores_location',
    'room_type_entire home/apt']

    # change the columns in df to match the columns in the model
    df = df.reindex(columns=order_cols, fill_value=0)
    
    model = load_model()
    # get predictions 
    y_pred = model.predict(df)

    return y_pred