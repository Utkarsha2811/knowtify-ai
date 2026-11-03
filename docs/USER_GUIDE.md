# Knowtify AI User Guide

Use Knowtify AI to create study aids from your own course material.

## Before you begin

You need:

- a running Knowtify backend and frontend
- one `.pdf`, `.txt`, or `.md` file
- a file smaller than 10 MB

Text-based PDFs work best. Scanned pages are images and require OCR, which this version does not provide.

## Protect sensitive information

Do not upload confidential, customer, or personal data. When OpenAI mode is enabled, selected passages are sent to the configured OpenAI API for generation. Use only data and AI services that you are authorized to use.

## Prepare a document

1. Open Knowtify in your browser.
2. Drag a supported file into **Add your material**, or click the upload area and select a file.
3. Check that the displayed file name is correct.
4. Select **Prepare document**.
5. Wait for the message confirming how many passages were prepared.

**Expected result:** The second panel becomes active and shows the available study tools.

## Create revision notes

1. Select **Summary**.
2. Enter a focus topic, or keep `overall revision`.
3. Select **Generate Summary**.
4. Review each note against the original document.

## Create flashcards

1. Select **Flashcards**.
2. Choose the number of cards.
3. Select **Generate Flashcards**.
4. Click a card to reveal its answer.

## Create a practice quiz

1. Select **Quiz**.
2. Choose the number of questions.
3. Select **Generate Quiz**.
4. Answer each question before selecting **Reveal answer**.

## Review generated content

AI-generated content can omit context or phrase a claim incorrectly. Before using or sharing it:

1. Compare key claims with the uploaded source.
2. Confirm that terminology matches the source.
3. Check every quiz answer.
4. Correct unclear wording.

For a repeatable review, use the [human review checklist](HUMAN_REVIEW_CHECKLIST.md).

## Troubleshooting

### The frontend cannot reach the backend

Confirm that Flask is running at `http://localhost:5000`. Then refresh the browser.

### A PDF contains no useful text

The PDF may contain scanned images. Export it with OCR or upload a text version.

### The output looks basic

Check `GET http://localhost:5000/api/health`. If `generation_mode` is `local-demo`, add a valid OpenAI API key to `backend/.env` and restart Flask.

### An upload is rejected

Confirm that the file uses a supported extension and is smaller than 10 MB.
