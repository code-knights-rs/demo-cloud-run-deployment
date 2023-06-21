from flask import Flask, render_template, request, session
from transformers import MarianMTModel, MarianTokenizer
import pandas as pd
import os
from google.cloud.sql.connector import Connector
import sqlalchemy

# Hydrate the environment from the .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'flask_secret_key'

connector = Connector()

# configure Cloud SQL Python Connector properties
def getconn():
    conn = connector.connect(
        os.environ["INSTANCE_NAME"],
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"]
    )
    return conn



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
    # create connection pool to re-use connections
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    with pool.connect() as db_conn:
        # create ratings table in our sandwiches database

        # insert data into our ratings table
        insert_stmt = sqlalchemy.text(
            "INSERT INTO demo_dataset (Input_text, Processed_text, Corrected_text, Ratings) VALUES (:Input_text, :Processed_text, :Corrected_text, :Ratings)",
        )

        # insert entries into table
        db_conn.execute(insert_stmt, parameters={"Input_text": row1, "Processed_text": row2,
                                                 "Corrected_text": row3, "Ratings": row4})

        # db_conn.execute(insert_stmt, parameters={"Input_text": "Hello World", "Processed_text": "hi-gaku",
        #                                          "Corrected_text": "hi-gaku", "Ratings": 1})

        # commit transactions
        db_conn.commit()

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