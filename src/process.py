import cv2
from pytesseract import image_to_string
import nltk
from nltk.corpus import stopwords
from deep_translator import GoogleTranslator
import numpy as np
import spacy
import sqlite3
import genanki
import re
import io

nlp = spacy.load("de_core_news_md")
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_image(file):
    img = cv2.imdecode(file, cv2.IMREAD_COLOR)[...,0]
    blured1 = cv2.medianBlur(img,3)
    blured2 = cv2.medianBlur(img,51)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255*divided/divided.max())
    _, threshed = cv2.threshold(normed, 100, 255, cv2.THRESH_OTSU)
    return threshed

def ocr_image(image_path, language='german'):
    if language == 'german':
        language = 'deu'
    preprocessed_img = preprocess_image(image_path)
    config = f"-l {language} --psm 1 --oem 3"
    text = image_to_string(preprocessed_img, config=config)
    return text

def preprocess_text(text, language='german'):
    tokens = nltk.word_tokenize(text)
    alphabetical_tokens = [token for token in tokens if token.isalpha()]
    lowercase_tokens = [token.lower() for token in alphabetical_tokens]
    stop_words = set(stopwords.words(language))
    filtered_tokens = [token for token in lowercase_tokens if token not in stop_words]
    unique_words = list(set(filtered_tokens))
    
    
    lemmatized_words = []
    for word in unique_words:
        doc = nlp(word)
        lemmatized_word = doc[0].lemma_
        if (lemmatized_word not in stop_words) and (lemmatized_word.isalpha()) and (len(lemmatized_word) > 2):
            lemmatized_words.append(lemmatized_word)
        else:
            pass

    return list(set(lemmatized_words))

def translate_words(word, source_language = 'german', target_language='english'):
    if source_language == 'german':
        source_language = 'de'
    if target_language == 'english':
        target_language = 'en'
    translation = GoogleTranslator(source=source_language, target=target_language).translate(word)
    
    return translation


def search_by_german_word(connection, german_word):
    cursor = connection.cursor()
    # Search for an exact match or a match without the article, including the additional information
    cursor.execute('''SELECT * FROM translations
                      WHERE german_word = ? OR german_word LIKE ? OR german_word LIKE ? OR german_word LIKE ?
                      OR german_word LIKE ? OR german_word LIKE ? OR german_word LIKE ?''',
                   (german_word, 'der ' + german_word, 'die ' + german_word, 'das ' + german_word,
                    '%' + german_word + '%', '%' + german_word + '%', '%' + german_word + '%'))
    results = cursor.fetchall()
    return results

def search_by_german_word_new(connection, german_word):
    cursor = connection.cursor()
    # Remove the articles from german_word column and compare with the input word
    cursor.execute('''
        SELECT * FROM translations
        WHERE REPLACE(REPLACE(REPLACE(german_word, 'der ', ''), 'die ', ''), 'das ', '') LIKE ?
    ''', ('%' + german_word + '%',))
    results = cursor.fetchall()
    return results

def get_words_and_translations(words, db_path, current_level = 'A1', languages = ['german', 'english']):
    connection = sqlite3.connect(db_path)
    a1_list = []
    a2_list = []
    b1_list = []
    extra_list = []
    tmp = set()

    for word in words:
        matched = search_by_german_word(connection, word)
        if matched:
            for matchh in matched:
                if (matchh[-1] == "A1") and word not in tmp:
                    a1_list.append((re.sub(r'[^,\w\s]', '', matchh[1]).split(", ")[0], matchh[3]))
                    tmp.add(word)
                elif (matchh[-1] == "A2") and word not in tmp:
                    a2_list.append((re.sub(r'[^,\w\s]', '', matchh[1]).split(", ")[0], matchh[3]))
                    tmp.add(word)
                elif (matchh[-1] == "B1") and word not in tmp:
                    b1_list.append((re.sub(r'[^,\w\s]', '', matchh[1]).split(", ")[0], matchh[3]))
                    tmp.add(word)
        elif (word not in tmp):
            translated = translate_words(word, languages[0], languages[1])
            extra_list.append((word, translated))
            tmp.add(word)
        else:
            pass
    match current_level:
        case 'A2':
            words_and_translations = list(set(a2_list + b1_list + extra_list))
        case 'B1':
            words_and_translations = list(set(b1_list + extra_list))
        case 'B2':
            words_and_translations = list(set(extra_list))
        case _:
            words_and_translations = list(set(a1_list + a2_list + b1_list + extra_list))

    return words_and_translations

def create_anki_deck(words_translations, deck_name):
    words, translations = zip(*words_translations)
    my_deck = genanki.Deck(
    1782664737,
    deck_name)

    style = """
    .card {
     font-family: times;
     font-size: 30px;
     text-align: center;
     color: black;
     background-color: white;
    }"""

    for word, translation in zip(words, translations):
        note = genanki.Note(
            model=genanki.Model(
                1607392319,
                'Simple Model',
                fields=[
                    {'name': 'Question'},
                    {'name': 'Answer'},
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '{{Question}}',
                        'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                    },
                ], css = style),
            fields=[word, translation])
        my_deck.add_note(note)

    deck = io.BytesIO()
    genanki.Package(my_deck).write_to_file(deck)
    return deck
