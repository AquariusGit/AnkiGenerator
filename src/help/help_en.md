# Anki Deck Generator - User Manual

Welcome to the Anki Deck Generator! This tool is designed to help you easily and efficiently create bilingual Anki learning cards with audio, screenshots, and original text from your favorite videos and subtitles.
The code is based on the business-friendly Apache open-source license, and the source code address is https://github.com/AquariusGit/AnkiGenerator.

## Table of Contents
- [Software Introduction](#software-introduction)
- [Main Features](#main-features)
- [System Requirements](#system-requirements)
- [First Use](#first-use)
- [Interface Overview](#interface-overview)
- [Usage Steps](#usage-steps)
  - [Step One: Download Audio/Video and Subtitles](#step-one-download-audiovideo-and-subtitles)
  - [Step Two: Generate Anki Deck](#step-two-generate-anki-deck)
  - [Optional: Generate from CSV File](#optional-generate-from-csv-file)
- [Configuration Tab](#configuration-tab)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)

---

## Software Introduction

This tool is a graphical interface application that can download video/audio and multi-language subtitles from video websites like YouTube, and process them into `.apkg` files that can be imported into Anki. The generated cards can include original sentences, translations, corresponding audio clips, video screenshots, and even automatically add pinyin/furigana/romanization for Chinese, Japanese, and Korean languages, greatly enriching your language learning materials.

## Main Features
- **Video Download**: Supports downloading videos or pure audio from websites like YouTube.
- **Subtitle Download**: Automatically fetches and downloads official subtitles and auto-generated subtitles.
- **Bilingual Cards**: One-click generation of Anki cards containing two language subtitles.
- **Audio Extraction**: Automatically extracts audio segments corresponding to each subtitle from the video.
- **Video Screenshot**: Automatically captures video frames for each card.
- **TTS Support**: When no video or audio is available, gTTS or Edge-TTS can be used to generate speech for subtitles.
- **Automatic Pronunciation Guides**:
    - Automatically adds Furigana for Japanese Kanji.
    - Automatically adds Pinyin for Chinese characters.
    - Automatically adds Romanization for Korean.
- **Highly Customizable**:
    - Customize Anki card templates and styles.
    - Adjust subtitle timeline, merge subtitle lines.
    - Multiple post-processing options, such as automatic cleanup of temporary files.
- **Multi-language Interface**: Supports English, Simplified/Traditional Chinese, Japanese, Korean, Vietnamese, and other interface languages.

## System Requirements
- **Python**: Python 3.x environment is required.
- **FFmpeg**: **FFmpeg** must be installed and added to your system's environment variable (PATH). FFmpeg is used to extract audio and capture screenshots from videos. If not installed correctly, related functions will not be available.

## First Use
When you run this software for the first time, an "Initial Setup" window will pop up.
1. **Select Display Language**: Choose the language you want the software interface to display.
2. **Select Default Front/Back Language**: Set your most frequently used source language (front) and target language (back). This will automatically select languages for you in subsequent operations, improving efficiency.
After setup, click "Continue" to enter the main interface.

## Interface Overview
The main software interface is divided into three main parts:
1. **Left - Function Tabs**:
    - **Download Audio/Video and Subtitles**: Download materials from a network URL.
    - **Generate Anki Deck**: Generate cards using local or downloaded materials.
    - **Generate Cards from CSV**: Batch generate cards from a `.csv` file.
    - **Configuration**: Set up the software's default behavior and Anki templates.
2. **Right - Log Window**: Displays all information, warnings, and errors during software operation.
3. **Bottom - Progress Bar**: Displays the progress of download or generation.

## Usage Steps

### Step One: Download Audio/Video and Subtitles
This tab is used to obtain the necessary materials for creating cards from online videos. However, please note that it is best if the video or audio contains only a single language, such as pure Chinese or pure Japanese. Do not use videos or audio that contain multiple languages simultaneously. For example, a video that first reads Chinese and then Japanese is not suitable. We will consider providing such functionality later.

1. **Video URL**: Paste a YouTube video link. The software will automatically detect valid links in the clipboard and fill them in. Usually, it's a single video file, not a playlist or a personal video page (which would lead to incorrect downloads or too many files being downloaded). By default, only YouTube videos are supported. If you want to use videos from other websites, check the box after the URL input field to indicate that the URL format should not be checked, then you can download audio/video and subtitles from any website supported by yt-dlp (please verify the results yourself).
2. **Query Language**: Click this button, and the software will start analyzing the URL to get all available video/audio formats and subtitle languages.
3. **Download Directory**: Select the folder where you want to save the downloaded files.
4. **Audio/Video Format**: Select a format from the dropdown list. It is recommended to choose `mp4` format which includes both audio and video, or `m4a` format for pure audio.
5. **Front/Back Subtitle Language**: Select the subtitle languages you want to use for the front and back of the card, respectively. The software will automatically try to select the default language based on your "Configuration".
6. **Download Subtitles Only**: If you already have video files locally, or do not want to generate screenshots and original audio, you can check this option to download only subtitle files.
7. **Start Download**: Click to start the download. After completion, the software will ask if you want to automatically fill the downloaded file paths into the "Generate Anki Deck" tab. It is recommended to choose "Yes".

### Step Two: Generate Anki Deck
This tab is where the core functionality lies, used to combine materials into Anki cards.

1. **File Path Settings**:
    - **Media File (Optional)**: Select your video or audio file. This is required if you want to extract audio and screenshots from the video.
    - **Front/Back Subtitle Files**: Select subtitle files for two languages (`.srt` or `.vtt` format).
    - **Output Directory**: Select the location to save the generated Anki deck (`.apkg`) and temporary files (if the directory does not exist, it will be created automatically).
    - **Anki Deck Name**: Name your Anki deck, by default it will be the same as the front subtitle filename.

2. **Main Options**:
    - **Screenshot Options**:
        - `Add Screenshot`: Check this to generate a screenshot for each card.
        - `Screenshot Time Point`: Choose to take the screenshot at the beginning, middle, or end of the subtitle.
        - `Quality`: Screenshot quality, between 1-31, smaller number means higher quality (and larger file size).
    - **TTS Engine**: Which engine to use to generate speech when no media file is available or audio extraction fails. `gTTS` requires connection to Google services, please confirm if it is available. Both `gTTS` and `edge-tts` are good choices. `Do not generate MP3` disables this function. `gTTS` requires connection to Google services, please confirm if it is available.
    - **Slow Speech**: If checked, gTTS will generate speech at a slower speed (edge-tts does not support this).
    - **Subtitle Cleanup**: Checking `Remove... non-dialogue content` will automatically delete content like `[Music]`, `(Applause)` from subtitles.
    - **Pronunciation Guide Options**: Check this to add pronunciation guides for Chinese/Japanese/Korean on the front or back.
    - **Post-processing**:
        - `Clean .mp3/.jpg/.csv files`: If checked, temporary audio, screenshots, and data files generated during the process will be automatically deleted after the Anki deck is successfully generated.
    - **Timeline Offset (ms)**: If there is a fixed delay between audio and subtitles, enter the milliseconds here to correct it (positive number makes audio earlier, negative number makes audio later).
    - **Subtitle Time Range**: If you only want to create cards for a specific part of the video, enter the start and end times here (format `HH:MM:SS`).
    - **Subtitle Merging**:
        - `Merge closely timed subtitle lines`: If checked, short subtitle lines with very close time intervals will be merged into one sentence, suitable for processing dialogue-intensive videos. Use this function with caution, it is not yet mature, and is only suitable for podcast-like media with irregular intervals.
        - `Maximum Interval (ms)`: Defines how close subtitles can be merged.
    - **File Handling**:
        - `Overwrite existing Anki deck`: If checked, if a file with the same name already exists in the output directory, it will be overwritten directly.

3. **Generate and Preview**:
    - **Preview first 5 cards**: Quickly generate an HTML file without generating the full deck to preview the effect of the first 5 cards in a browser. The preview does not include audio and preview images.
    - **Generate Anki Deck**: Click to start the final generation process.

### Optional: Generate from CSV File
If you already have organized bilingual comparison text, you can use this function to quickly create cards.

1. **Prepare CSV File**: Create a `.csv` file, with the **first column** as the front text of the card and the **second column** as the back text of the card. It must be UTF-8 encoded. If you need TTS to generate speech, do not add pronunciation guides or other content.
2. **CSV File**: Select your prepared CSV file in the software.
3. **Settings Options**: Similar to the "Generate Anki Deck" tab, you can set the output directory, deck name, TTS engine, and pronunciation guide options. Please ensure that the selected front and back languages are consistent with the CSV file, otherwise, it may lead to incorrect pronunciation.
4. **Generate Anki Deck**: Click the button to start generation. In this mode, there will be no audio extraction and screenshot functions, and audio will be entirely generated by TTS.

## Configuration Tab
Here you can customize the software's default behavior and card appearance.

- **Default Front/Back Subtitle Language**: Set your most frequently used languages, and the software will prioritize them during "Download" and "Auto-fill".
- **Anki Templates and Styles**:
    - **Front/Back Template**: Use Anki's template syntax (e.g., `{{Question}}`, `{{Audio_Answer}}`) to customize the layout of the front and back of the card.
    - **Stylesheet**: Use CSS code to customize the font, color, background, and other appearances of the card.
- **Preview HTML Template**: Customize the basic structure of the HTML file generated when clicking the "Preview" button. Generally, it is not recommended to modify this.
- **Save and Restore**:
    - `Save Configuration`: Save all your changes to the above settings.
    - `Restore Configuration`: Undo changes and restore to the last saved state.

## Frequently Asked Questions (FAQ)
1. **Q: What should I do if the software prompts "FFmpeg not found"?**
    A: You need to download it from the FFmpeg official website, extract it, add the full path of its `bin` directory to your operating system's `PATH` environment variable, and then restart the software.

2. **Q: Why is the YouTube link I pasted invalid?**
    A: This tool currently only supports single video URLs, not playlist URLs. Please ensure that your link does not contain the `list=` parameter. If you confirm that you want to use videos from other websites or use the software as a yt-dlp UI, then check the box after the URL address to force disable URL checking.

3. **Q: Which languages are supported for the pronunciation guide function?**
    A: Currently, it supports adding Furigana for Japanese, Pinyin for Chinese, and Romanization for Korean. The software will automatically determine based on your selected subtitle filename or the default language in the configuration.

4. **Q: What is the difference between gTTS and edge-tts?**
    A: Both are text-to-speech engines. gTTS (Google Text-to-Speech) may be slightly slower but supports slow playback. edge-tts (Microsoft Edge Text-to-Speech) usually has more natural and higher-quality speech but does not support slow playback. You can choose according to your needs. If one engine fails, the software will automatically try the other.

5. **Q: Is there a problem with generating Anki decks using YouTube's automatic subtitles?**
    A: It's hard to say for sure. Because automatic subtitles may have many issues with sentence segmentation, which can lead to problems with both generated and extracted audio. Therefore, it is not highly recommended to use automatic subtitles; try to use subtitles provided by the creator whenever possible.