from flask import Flask, render_template, request, session
from transformers import MarianMTModel, MarianTokenizer
import pandas as pd
import os
import sqlalchemy
import psycopg2
# Hydrate the environment from the .env file
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = 'flask_secret_key'


def init_db_connection():
    db_config = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_timeout': 30,
        'pool_recycle': 1800,
    }
    return init_unix_connection_engine(db_config)


def init_unix_connection_engine(db_config):
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="postgres+pg8000",
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            username=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME'),
        ),
        **db_config
    )
    pool.dialect.description_encoding = None
    return pool


db = init_db_connection()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/next', methods=['POST'])
def next_function():
    input_text = request.form['text1']
    processed_output = inference(input_text)

    row1 = input_text
    row2 = processed_output

    session['row1'] = row1
    session['row2'] = row2

    return render_template('result.html', result=processed_output)


@app.route('/translate', methods=['POST'])
def translate_function():
    row1 = session.get('row1')
    row2 = session.get('row2')

    corrected_text = request.form['text1']
    print(corrected_text, row2)
    row3 = corrected_text

    if row2 != corrected_text:
        row4 = 0
    else:
        row4 = 1

    data = {
        'Input_text': [row1],
        'Processed_output': [row2],
        'Corrected_text': [row3],
        'Ratings': [row4]
    }
    df = pd.DataFrame(data)
    print(df)

    # insert statement (DML statement for data load)
    insert_stmt = sqlalchemy.text(
        "INSERT INTO demo_dataset (Input_text, Processed_text, Corrected_text, Ratings) VALUES (:Input_text, :Processed_text, :Corrected_text, :Ratings)",
    )

    # interact with Cloud SQL database using connection pool
    with db.connect() as conn:
        # Insert data into Table
        conn.execute(insert_stmt).fetchone()

    return render_template('index.html', result=corrected_text)


def inference(text):
    # Download the model and tokenizer
    model_name = "models/opus-mt-en-de"  # English to German translation model
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text


if __name__ == '__main__':
    app.run(debug=True)