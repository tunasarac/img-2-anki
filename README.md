# Img-2-Anki Web App

The Img-2-Anki Web App is a simple tool that allows users to upload a series of images containing text, process them, and generate vocabulary flashcards. It's designed to assist language learners in generating digital flashcards ina convenient way.

## Features

- Upload a series of images for processing.
- Select the source language and target language (currently supports German to English).
- Specify your current language level to filter the generated flashcards.
- Process the images to extract unique words.
- Generate flashcards based on the filtered word list.
- Download flashcards as a CSV file for easy reference or as an Anki-compatible APKG deck for direct import.

## Usage

To use the Img-2-Anki Web App, follow these steps:

1. Access the web app by visiting --> [img-2-anki](https://img2anki-i7wnwki2yq-lm.a.run.app).
2. Choose the source language and target language from the provided options.
3. Select your current language level.
4. Upload a series of images containing text.
5. Wait for the images to be processed. This might take some time depending on the number of images uploaded.
6. Once the processing is complete, the flashcards will be displayed on the screen.
7. Download the flashcards in the desired format:
   - To download as a CSV file, click on the "Download CSV" button.
   - To download as an Anki-compatible APKG file, click on the "Download APKG" button.
   
   **Important Note:** The APKG file follows a specific behavior in Anki. When you import a new APKG file with the same deck_id as a previous deck, Anki will merge the new deck into the existing one. This means that any duplicate words will be removed, keeping only the new words from the second deck. This behavior is intentional to prevent redundancy and keep your study materials up to date.

8. Start studying and reinforcing your vocabulary using the downloaded flashcards.

## Current Limitations

Please be aware of the following limitations of the app:

- The maximum number of images that can be uploaded is currently limited to 10.
- Only German to English translation is supported at the moment.

## Contributing

Contributions to the Img-2-Anki are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.
