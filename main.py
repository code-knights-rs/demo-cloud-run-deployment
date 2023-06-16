from flask import Flask, render_template, request
from flask_mobility import Mobility
from transformers import MarianMTModel, MarianTokenizer

app = Flask(__name__)
Mobility(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    output = ""
    if request.method == 'POST' and  request.MOBILE:
        text = request.form['text']        # Process the form data
        result = inference(text=text)
        output = render_template('mobile_template.html', result=result)

    if request.method == 'POST' and not request.MOBILE:
        text = request.form['text']  # Process the form data
        result = inference(text=text)
        output = render_template('desktop_template.html', result=result)

    return output


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
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
