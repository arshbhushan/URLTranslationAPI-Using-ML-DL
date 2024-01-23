from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from deep_translator import GoogleTranslator
import os
from werkzeug.utils import url_quote
app = Flask(__name__)

def extract_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust the CSS selectors to match the structure of the site you are scraping
        main_content = soup.select_one('main').get_text()
        return main_content
    except Exception as e:
        return f"Error: {e}"

def translate_text(input_text, target_language='hi'):
    def translate_chunk(chunk):
        """Wrapper for Google Translate with character limit workaround."""
        translate = GoogleTranslator(source='auto', target=target_language).translate
        translated_text = ''
        source_text_chunk = ''

        for sentence in chunk.split('. '):
            sentence = sentence.strip()  # Remove leading/trailing whitespaces
            if len(sentence.encode('utf-8')) + len(source_text_chunk.encode('utf-8')) < 5000:
                source_text_chunk += '. ' + sentence if source_text_chunk else sentence
            else:
                translated_chunk = translate(source_text_chunk)
                translated_text += ' ' + translated_chunk if translated_chunk else ''
                
                if len(sentence.encode('utf-8')) < 5000:
                    source_text_chunk = sentence
                else:
                    message = '<<Omitted Word longer than 5000 bytes>>'
                    translated_text += ' ' + translate(message)
                    source_text_chunk = ''

        if source_text_chunk:
            translated_chunk = translate(source_text_chunk)
            translated_text += ' ' + translated_chunk if translated_chunk else ''

        return translated_text.strip()  # Remove leading/trailing whitespaces

    try:
        # Translate the input text
        translated_text = translate_chunk(input_text)

        # Return the translated text
        return translated_text
    except Exception as e:
        return str(e)

@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        url = request.form['url']
        target_language = request.form['language']

        content = extract_content(url)
        translated_content = translate_text(content, target_language)

        result = {
            'content': content,
            'translated_content': translated_content
        }

        return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
