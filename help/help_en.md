# Anki Card Package Generator - User Manual

Welcome to the Anki Card Package Generator! This tool is designed to help you easily and efficiently create bilingual Anki learning cards with audio, screenshots, and original text from your favorite videos and subtitles.
You can also quickly generate bilingual Anki learning cards (with audio) from your own treasured words or example sentences in CSV format.
The code is based on the business-friendly Apache open-source license, with the source code available at [https://github.com/AquariusGit/AnkiGenerator](https://github.com/AquariusGit/AnkiGenerator).

## Table of Contents
- [Software Introduction](#software-introduction)
- [Main Features](#main-features)
- [System Requirements](#system-requirements)
- [First-Time Use](#first-time-use)
- [Interface Overview](#interface-overview)
- [Usage Steps](#usage-steps)
  - [Step 1: Download Audio/Video and Subtitles](#step-1-download-audiovideo-and-subtitles)
  - [Step 2: Generate Anki Card Package](#step-2-generate-anki-card-package)
  - [Optional: Generate from CSV File](#optional-generate-from-csv-file)
- [Configuration Tab](#configuration-tab)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)

---

## Software Introduction

This tool is a graphical interface application that can download videos/audios and multilingual subtitles from video websites such as YouTube, and process them into `.apkg` files that can be imported into Anki. The generated cards can include original text, translations, corresponding audio clips, video screenshots, and even automatically add pinyin/furigana for multiple languages such as Chinese, Japanese, and Korean, greatly enriching your language learning materials.

## Main Features
- **Video Download**: Supports downloading videos or pure audio from websites such as YouTube.
- **Subtitle Download**: Automatically retrieves and downloads official subtitles (because YouTube doesn't allow anonymous download of auto-generated subtitles, please refer to the FAQ section for support on this feature).
- **Bilingual Cards**: One-click generation of Anki cards with two-language subtitles.
- **Audio Extraction**: Automatically extracts audio clips corresponding to each subtitle from the video.
- **Video Screenshots**: Automatically captures video frames for each card, or downloads from the web.
- **CSV Support**: Generate TTS audio and Anki cards from two-column CSV format files.
- **TTS Support**: When there are no videos or audios, use tools like gTTS or Edge-TTS to generate audio for subtitles.
- **Automatic Phonetic Annotation**:
    - Automatically adds furigana for Japanese kanji.
    - Automatically adds pinyin for Chinese characters.
    - Automatically adds romanization for Korean.
- **Highly Customizable**:
    - Customize Anki card templates and styles.
    - Adjust subtitle timelines.
    - Multiple post-processing options, such as automatic cleanup of temporary files.
- **Multi-language Interface**: Supports multiple interface languages including English, Simplified/Traditional Chinese, Japanese, Korean, Vietnamese, and more.

## System Requirements
- **Python**: Requires installation of Python 3.x environment.
- **FFmpeg**: Optional installation of **FFmpeg**, and add it to the system's environment variable (PATH). FFmpeg is used to extract audio from videos and take screenshots. If not properly installed, related features will not be available. If you confirm that you won't install FFmpeg, please don't select `original` audio when using the tool.

## First-Time Use
When you run this software for the first time, it defaults to the current system language. If the current system language isn't supported, it will switch to English.

## Interface Overview
The main interface of the software is divided into three main sections:
 
1.**Left - Function Tabs**: 

- **Download Audio/Video and Subtitles**: Download materials from YouTube.
- **Generate Anki Package with Subtitles**: Use local or downloaded materials to generate cards.
- **Generate Cards with CSV**: Batch generate cards from a `.csv` file.
- **Configuration**: Set default behaviors and Anki templates for the software.

2.**Right - Log Window**: Displays all information, warnings, and errors during the software's operation.

3.**Bottom - Progress Bar**: Shows the progress of downloading or generation.

## Usage Steps

### Step 1: Download Audio/Video and Subtitles
This tab is used to obtain materials needed for making cards from online videos. However, please note that the video or audio should preferably contain only a single language, such as pure Chinese or pure Japanese. Don't use videos or audio that contain multiple languages simultaneously. For example, videos that read Chinese first and then Japanese are not very appropriate.

1.  **Video URL**: Please enter a YouTube video link. This link is usually for a single video file and cannot be a playlist or a personal video page (this will cause incorrect downloads or download too many files). By default, only YouTube videos are supported. If you want to use videos from other websites, please check the checkbox after the URL input box, indicating that the URL format will not be checked, allowing you to download audio/video and subtitles from any website supported by yt-dlp (results to be confirmed by you).
2.  **Query Language**: Click this button, and the software will start analyzing the URL to get all available video/audio formats and subtitle languages.
3.  **Download Directory**: Select the folder where you want to save the downloaded files. If it doesn't exist, it will usually be created automatically.
4.  **Audio/Video Format**: Select a format from the drop-down list. It's recommended to choose the `mp4` format that includes both audio and video, or the `m4a` format for pure audio.
5.  **Front/Back Subtitle Language**: Select the subtitle languages you want to use for the front and back of the card, respectively. The software will automatically try to select the default language according to your `configuration`.
6.  **Download Subtitles Only**: If you already have local video files, or don't want to generate screenshots and original audio, you can check this option to download only subtitle files.
7.  **Start Download**: Click to start the download. After completion, the software will ask if you want to automatically fill the downloaded file paths into the `Generate Anki Package` tab. It's recommended to select `Yes`.

### Step 2: Generate Anki Card Package Based on Subtitles
This tab is where the core functionality lies, used to combine materials such as subtitles and videos into an Anki card package.

1.  **File Path Settings**:
    - **Media File (Optional)**: Select your video or audio file. This is required if you want to extract audio and screenshots from the video.
    - **Front/Back Subtitle Files**: Select subtitle files in two languages (`.srt` or `.vtt` format).
    - **Output Directory**: Select the location to store the generated Anki package (`.apkg`) and temporary files (if the directory doesn't exist, it will be created automatically).
    - **Anki Package Name**: Name your Anki card package, defaulting to the same as the front subtitle file name.

2.  **Main Options**:
    - **Screenshot Options**:
        - `Add Screenshots`: Checking this will generate screenshots for each card (the source is specified by the user, which may be a video screenshot, or the first image obtained through keyword searches on search engines like Google/Baidu/Bing). This option is not only extremely slow in generation (with a large number of network requests and a higher chance of failure), but also causes the generated Anki card package to take up an extremely large amount of space, so please consider carefully before using this feature.
        - `Screenshot Timing`: If it's a video screenshot, select whether to take the screenshot at the beginning, middle, or end of the subtitle.
        - `Quality`: Screenshot quality, between 1-31, the smaller the number, the higher the quality (and the larger the file).
    - **TTS Engine**: Which engine to use to generate audio when there are no media files or audio extraction fails. Both `gTTS` and `edge-tts` are good choices, while pyttsx3 uses local TTS functionality, which is fast but slightly less effective. `Don't generate MP3` means no audio is generated. For `gTTS` and `edge-tts`, please confirm for yourself whether they are available (you can verify by accessing Google's website). If uncertain, it's recommended to use pyttsx3.
    - **Slow Audio**: When checked, gTTS will generate audio at a slower speed (other TTS options currently don't support this).
    - **Subtitle Cleanup**: Checking `Remove... non-dialogue content` will automatically delete content such as `[Music]`, `(Applause)` in the subtitles.
    - **Phonetic Options**: When checked, phonetic annotations will be added to the Chinese/Japanese/Korean text on the front or back.
    - **Timeline Offset (ms)**: If there is a fixed delay between the audio and subtitles, enter the number of milliseconds to correct (positive numbers make the audio earlier, negative numbers delay the audio).
    - **Subtitle Time Period**: If you only want to make cards for a certain part of the video, enter the start and end times here (format `HH:MM:SS`).
    - **Cleanup**: After successfully generating the Anki package, intermediate files generated during the process will be automatically deleted, including temporary audio, screenshots, and data files.
    - **Override Target**: When checked, if a file with the same name already exists in the output directory, it will be overwritten directly.

3.  **Generation and Preview**:
    - **Preview**: Quickly generate an HTML file without generating a complete package to preview the effect in a browser. The preview doesn't include audio or preview images, only text (and phonetic annotations).
    - **Generate**: Click to start the final process of generating the Anki card package.

### Optional: Generate from CSV File
If you already have well-organized bilingual text, you can use this feature to quickly make cards.

1.  **Prepare CSV File**: Create a `.csv` file, with the **first column** being the front card text and the **second column** being the back card text. UTF-8 encoding must be used. If you need TTS to generate audio, please don't add phonetic annotations or other content.
2.  **CSV File**: Select your prepared CSV file in the software.
3.  **Setting Options**: Similar to the "Generate Anki Package" tab, you can set the output directory, package name, TTS engine, and phonetic options. Please ensure that the selected front and back languages match the CSV file, otherwise the pronunciation will be incorrect.
4.  **Generate**: Click the button to start generating the Anki package. In this mode, there will be no audio extraction or screenshot functions, and the audio will rely entirely on TTS generation.

When I was learning foreign languages before, I would collect various example sentences for easy memorization. But with the development of AI, it will become more convenient. For example, you can have AI assistants like Gemini, ChatGPT, or Kimi generate corresponding example sentences for learning. One of my learning methods is to generate multiple native language example sentences, and then generate 3 to 5 foreign language example sentences with the same meaning for each native language example sentence. This allows you to learn multiple expressions and, due to relevance, helps with efficient memorization. For example, when learning Japanese, I like to use the following prompt to have the AI assistant help me generate the corresponding CSV file: `Generate 10 sets of N3-level Japanese example sentences, each containing 1 Chinese translation and 3 Japanese expressions with similar meanings. When generating the CSV, put Chinese in the first column, separate the three Japanese expression sentences with line breaks, combine them, and put them in the second column, with the CSV file using " to represent the separator.`. The above prompt will generate corresponding content, which can be saved as a UTF-8 CSV file. If using AI assistants like Gemini CLI, you can also add a sentence after the prompt: `Finally, write to the n3.csv file and save it in UTF-8 format.` to directly obtain a perfect CSV file.


## Configuration Tab
Here you can customize the software's default behaviors and card appearance.

- **Language**: Set the language used for the current interface.
- **Default Front/Back Subtitle Language**: Set your most commonly used languages. The software will prioritize them as defaults when "downloading" and "generating Anki cards" (can be modified on the corresponding interface).
- **Default TTS**: Which TTS to use by default.
- **Network Request Interval**: `gTTS` and `edge-tts` call the services provided by the respective service providers online. These service providers usually require at least a 0.5s interval between two calls.
- **Anki Templates and Styles**:
    - **Front/Back Templates**: Use Anki's template syntax (such as `{{Question}}`, `{{Audio_Answer}}`) to customize the layout of the front and back of the card.
    - **Stylesheet**: Use CSS code to customize the font, color, background, and other appearances of the card.
- **Preview HTML Template**: Customize the basic structure of the HTML file generated when the "Preview" button is clicked. Generally, it's not recommended to modify.
- **Save and Restore**:
    - `Save Configuration`: Save all your changes to the above settings.
    - `Restore Configuration`: Revert changes and restore to the state saved last time.


## Frequently Asked Questions (FAQ)
1.  **Q: How do I install yt-dlp and FFmpeg?**
    A: FFmpeg is not mandatory, but if you need to extract content from audio/video, you need to install it. Download it from the [FFmpeg official website](https://ffmpeg.org/), extract it, add the full path of its `bin` directory to your operating system's environment variable `PATH`, and then restart this software.

2.  **Q: Why does my pasted YouTube link prompt as invalid?**
    A: This tool currently only supports single video URLs, not playlist (Playlist) URLs. Please ensure your link does not contain the `list=` parameter. If you confirm that you want to use videos from other websites or use the software as a yt-dlp UI, please check the checkbox after the URL address to force removal of URL checks.

3.  **Q: What languages does the phonetic function support?**
    A: Currently supports adding furigana for Japanese, pinyin for Chinese, and romanization for Korean. The software automatically determines based on the subtitle file name you select or the default language in the configuration. Because my own knowledge is limited, I don't know what other languages need phonetic annotations. If needed, you can submit an `issue` on `github`.

4.  **Q: What's the difference between gTTS, edge-tts, and pyttsx3?**
    A: All of the above are text-to-speech engines. gTTS (Google Text-to-Speech) may be slightly slower but supports slow playback. edge-tts (Microsoft Edge Text-to-Speech) typically has more natural and higher quality voice but doesn't support slow playback. You can choose according to your needs. pyttsx3 is a local voice engine, extremely fast, but may only support a limited number of languages. Therefore, when gtts and edge-tts are available, these two are prioritized. If one engine fails, the software will automatically try another.

5.  **Q: Are there any issues with using YouTube's auto-generated subtitles to create ANKI packages?**
    A: Because of auto-generated subtitles, there may be many issues with sentence breaks, which may cause problems with the generated audio and captured audio. I have tried multiple videos before, and none of them were very suitable. So it's not very recommended to use auto-generated subtitles; try to use subtitles provided by creators as much as possible.

6.  **Q: Why does the generated Anki package sometimes fail to import?**
    A: This is difficult to determine. Because I have encountered similar issues on my own computer, sometimes re-generating works, or importing on a mobile phone works correctly. If you can reproduce this issue, you can share the corresponding subtitle or CSV file, and I will try to fix it.

7.  **Q: How do I download YouTube's auto-generated subtitles?**
    A: First, install the `Get cookies.txt LOCALLY` extension, then export `cookies.txt`, and place it in the software directory, alongside `config.json`. When the software detects that `cookies.txt` exists, it will automatically enable downloading of YouTube's auto-generated subtitles. Note that YouTube's cookie validity period is 6 hours, and after timeout, it can't be guaranteed that auto-generated subtitles can be successfully downloaded. It's best to update cookies.txt before use.

8.  **Q: Are there any CSV example files?**
    A: There are four example CSV files in the `examples` directory. `cn-ja.csv` is an example with Chinese on the front and Japanese on the back. `en-cn.csv` is an example with English on the front and Chinese on the back. `cn-ja-multi.csv` is an example with Chinese on the front and multiple Japanese on the back. `en-cn-multi.csv` is an example with English on the front and multiple Chinese on the back. You can use these four files to experience the function of generating Anki card packages from CSV.

9.  **Q: Can dialects be supported?**
    A: Not supported for now, considering it for the future.

10. **Q: Can I specify male or female voice?**
    A: If using `edge-tts`, the default is male voice, while `gtts` defaults to female voice.

11. **Q: Some languages can't generate audio**
    A: Because I myself only know three languages: Chinese, English, and Japanese. Although many languages are supported by edge-tts and gtts, I really can't test all language support, so there might be errors. If you know how to code, you can find `_male_lang_to_voice` in the file `app/aquarius/service/tts_generator.py`, locate the corresponding language yourself, and check whether the `edge-tts` corresponding voice model is correct (although I have verified, there hasn't been complete testing, so I can't guarantee it). Or submit an `issue` on `github`.

12. **Q: Why aren't there audio/video formats when querying video information?**
    A: Because YouTube changes its rules from time to time, sometimes `yt-dlp` cannot correctly obtain the corresponding audio/video formats, so it's necessary to update `yt-dlp` regularly. If using the `run directly` approach, you can enter the `venv` directory in the main program directory and run `update_yt_dlp.bat` (Windows platform) or `update_yt_dlp.sh` (Linux/MacOS platform). After updating `yt-dlp`, restart the software and try again.