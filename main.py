from flask import Flask, render_template, request
from flask_mobility import Mobility
from transformers import MarianMTModel, MarianTokenizer

app = Flask(__name__)
Mobility(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    template = 'desktop_template.html'
    default_value = ""
    try:
        if request.method == 'POST' and request.MOBILE:
            template = 'mobile_template.html'
            text = request.form['text']  # Process the form data
            # result = ryu.ryu(english_sentence=text)
            result = inference(text=text)

        elif request.method == 'POST' and not request.MOBILE:
            template = 'desktop_template.html'
            text = request.form['text']  # Process the form data
            # result = ryu.ryu(english_sentence=text)
            if text:
                result = inference(text=text)
                print(text, result)
            text_res = request.form.get('input_text')
            # print(text_res)
            if text_res:
                print(text_res)

        return render_template(template, default_value=default_value, result=result)

    except Exception as error:
        return f"Error Encountered as: {error}"


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
