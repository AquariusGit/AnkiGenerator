[简体中文](README_zh_CN.md)

As a programmer learning Japanese, I discovered the amazing learning tool Anki. I've always wanted to import the large amount of data I've accumulated into Anki, but creating cards one by one manually was too tedious, so I never got around to it.
Recently, I've been thinking about how AI assistants can better collaborate with software development, so I decided to give it a try. With the help of an AI assistant, I used Python, a language I've never used before, to develop an application that can download YouTube audio/video and subtitles locally, and then use ffmpeg and TTS to generate corresponding Anki packages.
The prototype development was very fast, completed in less than a day. To my surprise, during the interaction with the AI assistant, it provided a lot of requirements that I then implemented in the program.
However, from an architect's perspective, the code modularity was not good. I guess the AI assistant still needs deeper learning and understanding.
So, after the first version was completed, I decided to re-implement the GUI using Qt and modularize the code with the help of AI.
The development process after this refactoring was: after layering, define corresponding interface protocols, then divide modules, and only give small functions under 100 lines of code to the AI to generate. The overall result is much better than the first version. I will try more AI collaboration practices in the future.
The corresponding instructions for use are below (the multi-language versions are generated and translated by AI, I only made minor modifications).

## How to Run
Prerequisite: Install [FFmpeg](https://ffmpeg.org/) first (optional, not necessary if you don't need to extract original audio).

### Method 1: Using the pre-compiled installation package
If you are a regular user, you can download the pre-compiled installation package from the project's Release page (currently only the Windows version is available), unzip it and run `AnkiGenerator.exe`.

### Method 2: Run directly (requires Python environment), this method is more recommended for users with coding or system experience (for easier upgrades)
If you are familiar with Python, please install Python 3.0 or above first (recommended `3.10`, not recommended `3.13` because `3.13` removed a built-in library, which may cause runtime errors), then unzip the downloaded zip file and run `run.bat` (use `run.sh` for linux/macos platforms), which will create a python venv environment in the current directory and automatically run `app/aquarius/main.py`.

## Help
If you need help, just press the F1 key to open the help file.
[English](help/help_en.md) [简体中文](help/help_zh_hans.md) [繁体中文](help/help_zh_hant.md) [日本語](help/help_ja.md) [한국어](help/help_ko.md)  [Tiếng Việt](help/help_vi.md)


![Download Tab](images/download_tab.png)

![Generate Anki package from subtitle](images/generate_from_subtitle.png)

![Generate Anki package from CSV](images/generate_from_csv.png)

![Configuration](images/configuration.png)
