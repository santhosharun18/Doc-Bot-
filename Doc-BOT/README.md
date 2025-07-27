# Doc-BOT Backend

**Doc-BOT** is a secure, AI-powered medical recommendation service. This repository implements a Flask REST API that powers:

- **Text-based chat** with a medical guidance model  
- **Text-to-Speech (TTS)** synthesis of AI responses  
- **Audio transcription** (speech-to-text) followed by AI response and TTS  

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Technology Stack](#technology-stack)  
4. [Prerequisites](#prerequisites)  
5. [Environment Configuration](#environment-configuration)  
6. [Installation](#installation)  
7. [Usage](#usage)  
   - [Running the API](#running-the-api)  
   - [Endpoints](#endpoints)  
8. [Error Handling](#error-handling)  
9. [Testing](#testing)  
10. [Contributing](#contributing)  
11. [License](#license)  

---

## Overview

The Doc-BOT backend provides a robust, production-ready API for an AI-driven medical chatbot. It integrates:

- **Google Gemini** for natural language understanding and response generation  
- **edge-tts** for high-quality speech synthesis  
- **SpeechRecognition** (Google Web Speech API) for audio transcription  
- **Flask** as the web framework, with CORS support for cross-origin clients  

All AI interactions are subject to a strict medical-only system prompt and adhere to HIPAA/GDPR principles for data privacy.

---

## Features

- **/chat**: Pure text chat endpoint  
- **/tts**: Text-to-speech endpoint (returns MPEG audio stream + AI text header)  
- **/transcribe**: Upload audio → speech-to-text → AI response → TTS audio  
- **CORS** enabled for browser-based front-ends  
- **Custom headers** expose AI replies and transcription results  

---

## Technology Stack

| Component                | Implementation                            |
|--------------------------|-------------------------------------------|
| Web Framework            | Flask                                     |
| AI Inference             | Google Gemini (`google-genai` SDK)        |
| Text-to-Speech           | edge-tts                                  |
| Speech Recognition       | SpeechRecognition (Google API)            |
| Audio Format Handling    | PyDub, ffmpeg                             |
| Security & Compliance    | CORS, JWT (optional), HIPAA/GDPR guidelines |

---

## Prerequisites

- **Python 3.11+**  
- **ffmpeg** installed and available on `PATH`  
- **Google GenAI API Key**  

---

## Environment Configuration

Create a `.env` file in the project root with:

```bash
GOOGLE_API_KEY=your_google_genai_api_key
FLASK_ENV=development
````

> **Security Note**
> Do **not** commit your `.env` file. Ensure `GOOGLE_API_KEY` is set in production.

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/SamuelJayasingh/Doc-BOT.git
   cd Doc-BOT
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install ffmpeg**

   * **macOS**: `brew install ffmpeg`
   * **Ubuntu**: `sudo apt-get install ffmpeg`
   * **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to `PATH`

---

## Usage

### Running the API

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=5000
```

Server will listen on `http://127.0.0.1:5000`.

### Endpoints

#### 1. POST `/chat`

* **Description**: Send user text, receive AI response.
* **Request Body** (JSON):

  ```json
  {
    "text": "I have a headache and fever.",
    "history": ""
  }
  ```
* **Response** (JSON):

  ```json
  {
    "response": "Your symptoms suggest a viral infection. Stay hydrated..."
  }
  ```

#### 2. POST `/tts`

* **Description**: Convert text (and optional chat history) into spoken audio.
* **Request Body** (JSON):

  ```json
  {
    "text": "Recommend treatment for migraine.",
    "history": ""
  }
  ```
* **Response**:

  * **Body**: MPEG audio stream
  * **Headers**:

    * `X-AI-Response`: AI’s plain-text reply
    * `Access-Control-Expose-Headers: X-AI-Response`

#### 3. POST `/transcribe`

* **Description**: Upload an audio file → transcribe → AI response → TTS audio.
* **Form-Data**:

  * `audio`: WAV or MP3 file
  * `history`: *optional* chat history
* **Response**:

  * **Body**: MPEG audio stream
  * **Headers**:

    * `X-Transcribed-Text`: recognized text
    * `X-AI-Response-Text`: URL-encoded AI reply
    * `Access-Control-Expose-Headers: X-Transcribed-Text, X-AI-Response-Text`

---

## Error Handling

All errors return JSON with an `"error"` field:

* **400 Bad Request**: missing or invalid parameters
* **500 Internal Server Error**: AI generation, TTS, or transcription failures

Example:

```json
{
  "error": "Text parameter is required"
}
```

---

## Testing

Use tools like **cURL**, **Postman**, or **HTTPie**. Example with cURL:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"text":"What is hypertension?","history":""}'
```

---

## Contribution

- If you have any suggestions to this README or about the Script, feel free to inform me. And if you liked, you are free to use it for yourself.(P.S. Star it too!! 😬 )

- Your Contributions are much welcomed here!
   > Fork the project
   > > Compile your work
   > > > Call in for a Pull Request

Credits: [Samuel Jayasingh](https://github.com/SamuelJayasingh)

Last Edited on: 19/05/2025

## License

This project is distributed under the **MIT License**. See [LICENSE](LICENSE) for full terms.


