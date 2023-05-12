from flask import Flask, render_template, request, redirect, flash, Response, url_for, send_file
import os
from werkzeug.utils import secure_filename
from src.process import *
import time
from dotenv import load_dotenv

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16MB
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.secret_key = os.getenv('SECRET_KEY')
progress = 0
study_cards = []

@app.route('/')
def index():
    global progress
    progress = 0  # reset progress at the start of every new request
    return render_template('index.html')

@app.route('/progress')
def get_progress():
    def generate():
        global progress
        while progress <= 100:
            yield f"data:{progress}\n\n"
            time.sleep(0.5)

    return Response(generate(), mimetype= 'text/event-stream')

@app.route('/upload', methods=['POST'])
def upload():
    global progress
    global study_cards
    files = request.files.getlist('file')
    level = request.form.get('option')
    language = request.form['language']
    target_language = request.form['target_language']
    languages = [language, target_language]
    del language, target_language

    # Limit number of files
    if len(files) > 10:
        flash('Too many files. Maximum 10 files are allowed.')
        return redirect(request.url)

    db_path = './database/words_by_level.db'
    for i, file in enumerate(files):
        if file:
            # Read file into memory
            file_bytes = file.read()
            npimg = np.frombuffer(file_bytes, np.uint8)
            text = ocr_image(npimg, languages[0])
            words = preprocess_text(text)
            study_cards.extend(get_words_and_translations(words, db_path, level, languages))
            progress = (i+1) / len(files) * 100
    return redirect(url_for('result'))

@app.route('/result')
def result():
    global study_cards
    return render_template('result.html', study_cards=study_cards)

@app.route('/download/csv')
def download_csv():
    global study_cards
    csv_data = '\n'.join([f'{card[0]},{card[1]}' for card in study_cards])
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=your-study-cards.csv'}
    )

@app.route('/download/apkg')
def download_apkg():
    global study_cards
    deck = create_anki_deck(study_cards, 'My Deck')
    deck.seek(0)
    return send_file(deck, as_attachment=True, download_name='your-anki-deck.apkg')


if __name__ == '__main__':
    server_port = int(os.environ.get('PORT', '8080'))
    app.run(debug=True, host='0.0.0.0', port=server_port)