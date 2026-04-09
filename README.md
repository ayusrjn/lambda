<p align="center">
  <img src="images/logo.png" alt="Lambda Logo" width="120">
</p>

<h1 align="center">Lambda</h1>

<p align="center">
  <strong>A minimal, function-driven coding agent designed for efficiency.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" alt="Maintained">
</p>

---
<p align="center">
  <img src="images/screen.png" alt="Lambda Logo" width="auto">
</p>

---
## Overview

**Lambda** is a powerful yet minimal coding agent built to streamline software development. It specializes in generating, debugging, and optimizing code with a focus on speed and accuracy.

## Key Features

- **Code Generation**: Instant high-quality code snippets from natural language.
- **Smart Debugging**: Identify and fix bugs with intelligent context analysis.
- **Optimization**: Refactor code for better performance and readability.
- **Extensible**: Designed to be integrated into various workflows and IDEs.

## Installation

Install Lambda directly from the repository using pip:

```bash
git clone https://github.com/ayusrjn/lambda.git
cd lambda
pip install .
```

> **Note**: For development, you can use `pip install -e .` instead.

## Usage

Simply run the agent from your terminal:

```bash
lambda
```

### First-Time Setup
When you run `lambda` for the first time, it will automatically prompt you to enter your [Gemini API Key](https://aistudio.google.com/app/apikey) and preferred model. These settings will be securely saved to `~/.config/lambda-agent/config.env`, allowing you to run the agent from anywhere on your system.

*(Optional)* You can still override these global settings on a per-project basis by creating a `.env` file in your current working directory.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

## Attribution

- Lambda icon by [shohanur.rahman13](https://www.flaticon.com/authors/shohanur-rahman13) from [Flaticon](https://www.flaticon.com/free-icons/lambda)
