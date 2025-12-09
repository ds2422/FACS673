# 🧠 Nexus AI - Multi-Source Content Summarizer

![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)
![Django](https://img.shields.io/badge/Backend-Django%20REST-green)
![Firebase](https://img.shields.io/badge/Database-Firebase-orange)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%201.5-purple)

**Nexus AI** is a powerful SaaS application designed to combat information overload. It aggregates content from up to **5 different sources**—including YouTube videos, PDF documents, web articles, and raw text—and uses Google's Gemini AI to synthesize them into a single, coherent summary.

---

## ✨ Key Features

- **Multi-Modal Input:** Process up to 5 inputs simultaneously.
  - **YouTube:** Automatically extracts transcripts (captions) from video URLs.
  - **PDF:** Extracts text from uploaded PDF documents.
  - **Web:** Scrapes and extracts main content from article URLs.
  - **Text:** Accepts raw text input.
- **Intelligent Synthesis:** Uses **Google Gemini 1.5 Flash** to find connections between disparate sources and generate a unified summary.
- **Modern UI/UX:** Built with **Glassmorphism** design principles using Tailwind CSS for a sleek, responsive experience.
- **User Management:** Secure Login/Registration via **Firebase Authentication**.
- **History Tracking:** Automatically saves user summaries to **Firestore** with a slide-out history sidebar.
- **Automated Testing:** BDD (Behavior Driven Development) test suite using **Behave** and **Selenium**.

---

## 🛠 Tech Stack

### Frontend

- **Framework:** React (Vite)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Auth:** Firebase SDK

### Backend

- **Framework:** Django (Python)
- **API:** Django REST Framework (DRF)
- **AI Model:** Google Generative AI (`google-generativeai`)
- **Processing:**
  - `pytubefix` (YouTube Transcripts)
  - `beautifulsoup4` (Web Scraping)
  - `pypdf` (PDF Parsing)
- **Database:** Firebase Admin SDK (Firestore)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- Node.js (v16+)
- Python (v3.10+)
- Google Cloud Project (with Firebase & Gemini API enabled)

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/nexus-ai.git
cd nexus-ai
```
