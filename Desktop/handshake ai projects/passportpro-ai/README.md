# PassportPro AI 📸✈️

**Professional AI-Powered Passport & ID Photo Studio with 1-Click Print Sheet Generation**

PassportPro AI is a full-stack web application and AI studio that transforms casual selfies, smartphone photos, and distant scenery shots into official, compliant passport-size photographs and ready-to-print photo sheets (JPG & PDF) in seconds.

---

## 🌟 Key Features

### ⚡ 1-Click AI Studio
- **One-Step End-to-End Pipeline**: Skip manual 5-step workflows. Upload any photo, pick your country and paper size, and instantly receive your processed passport photo and multi-copy print sheet.
- **Instant Downloads**: 1-click downloads for **Ready-to-Print PDF Document**, **High-Resolution Print Sheet (JPG)**, and **Single Passport Photo (JPG)**.

### 🌿 100% Natural Photo Quality (No Artificial "Oil-Color" Filters)
- **Authentic Skin Tones & Textures**: Retains your camera's real RGB colors, skin pores, and natural textures without plastic smoothing or muddy oil-paint artifacts.
- **Subtle Photographic Tone Curve**: Optional clarity and fine unsharp mask without color distortion or halo artifacts.

### 📐 Head Posture & Selfie Auto-Straightening
- **Eye-Level Alignment**: Automatically detects left and right eye coordinates, calculates the tilt angle ($\theta$), and rotates the image to achieve a level, upright posture ($0^\circ$ tilt).
- **Scenery & Long-Distance Photo Support**: Detects persons standing in wide scenes, living rooms, or outdoor photos, isolating the upper torso and head with standard passport proportions.

### 🖨️ 4×6 Print Sheet Generator (8 Photos Evenly Distributed)
- **Standard Photo Paper Layout**: Generates a balanced $4 \times 2$ grid (4 columns $\times$ 2 rows = 8 photos) on standard 4×6 inch ($152.4 \times 101.6\text{ mm}$ at 300 DPI) photo paper.
- **Uniform Margins & Cutting Guides**: Eliminates wasted borders with thin, clean printed cutting lines.
- **A4 Document Support**: Generates 4, 6, 8, 12, or 16 photo grids for standard A4 paper.

### ☁️ Optional Cloud AI API Support
- **OpenAI (ChatGPT / GPT-4o Vision API)**: Biometric validation, posture assessment, and compliance analysis.
- **Google Gemini 1.5 Flash Vision API**: High-speed multi-modal facial alignment.
- **Clipdrop / Stability AI API**: Studio-grade background removal and lighting.
- **Local Engine (Default)**: Works 100% locally and privately without requiring any API keys.

### 🛠️ Full Step-by-Step Customization
- **Step 1: Validation** — ICAO compliance score (head size, centering, lighting, background).
- **Step 2: Background Removal** — Solid white (`#FFFFFF`), off-white, light blue, light grey, or custom color.
- **Step 3: Enhancement** — Manual adjustments for brightness, contrast, exposure, and sharpness.
- **Step 4: Passport Sizing** — Over 100+ country specifications or custom mm/DPI dimensions.
- **Step 5: Print Sheet** — Custom grid arrangement and live preview.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11 / 3.12, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug
- **Computer Vision & AI**: OpenCV (`opencv-python-headless`), MediaPipe, NumPy, rembg (`u2net`), Pillow
- **Print & PDF Engine**: FPDF2 (with millimeter physical sizing)
- **Cloud APIs**: OpenAI REST API (GPT-4o Vision), Google Gemini API, Clipdrop API
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
- **Database**: SQLite (default / development) / PostgreSQL (production ready)

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.11 or 3.12
- Git

### 2. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/your-username/passportpro-ai.git
cd passportpro-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS / Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Configure Environment
Create or edit your `.env` file:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000
DATABASE_URL=sqlite:///passportpro.db

# Upload Settings
MAX_CONTENT_LENGTH=20971520
UPLOAD_FOLDER=uploads

# AI Settings
FACE_DETECTION_CONFIDENCE=0.5
BACKGROUND_MODEL=u2net

# Cloud AI API Keys (Optional - Can also be entered in the UI)
OPENAI_API_KEY=
GEMINI_API_KEY=
CLIPDROP_API_KEY=

# Default Admin
ADMIN_EMAIL=admin@passportpro.ai
ADMIN_PASSWORD=changeme123
```

### 5. Run Locally
```bash
python run.py
```
Open your browser and navigate to **`http://localhost:5000`**.

---

## 🐳 Docker & Render Deployment

### Run with Docker Locally
```bash
# Build the Docker image
docker build -t passportpro-ai .

# Run the container
docker run -p 5000:5000 --env-file .env passportpro-ai
```

### Deploy to Render
1. Push this repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New +** $\rightarrow$ **Web Service**.
3. Select your repository and choose **Docker** runtime (Render will automatically detect `Dockerfile` and `render.yaml`).
4. Set your environment variables (`SECRET_KEY`, `ADMIN_EMAIL`, etc.).
5. Click **Create Web Service**.

---

## 📁 Project Structure

```
passportpro-ai/
├── app/
│   ├── ai/
│   │   ├── face_detection/      # MediaPipe & Haar Cascade detector & analyzer
│   │   ├── background_removal/  # U2-Net background removal
│   │   ├── enhancement/         # Natural tone & studio photographic filters
│   │   └── quality_analysis/    # ICAO 100-point validation scorer
│   ├── models/                  # SQLAlchemy models (User, Photo, PhotoJob, CountryRequirement)
│   ├── routes/                  # Flask Blueprints (auth, dashboard, photos, processing, passport, downloads)
│   ├── services/                # Business logic & AI studio orchestration (AIStudioService, CloudAIService)
│   ├── static/                  # CSS, JS, branding assets
│   ├── templates/               # Jinja2 HTML templates (1-Click studio, camera, gallery, etc.)
│   ├── utils/                   # Image math, auto-straighten, precision crop & DPI helpers
│   ├── config.py                # App configuration
│   └── extensions.py            # SQLAlchemy, Migrate, LoginManager, CSRF
├── data/                        # Seed data (100+ country passport specifications)
├── uploads/                     # User photos (originals, thumbnails, processed - gitignored)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # Documentation
```

---

## 🌍 Supported Country Standards

| Country | Document Type | Dimensions | DPI | Head Size Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **United States** | Passport / Visa | $2 \times 2\text{ inches}$ ($51 \times 51\text{ mm}$) | 300 | 50% – 69% |
| **India** | Passport / Visa | $35 \times 45\text{ mm}$ | 300 | 70% – 80% |
| **India** | PAN Card / OCI | $25 \times 35\text{ mm}$ / $35 \times 35\text{ mm}$ | 300 | 60% – 75% |
| **United Kingdom** | Passport / Driving License | $35 \times 45\text{ mm}$ | 300 | 65% – 75% |
| **Schengen / EU** | Visa / Passport | $35 \times 45\text{ mm}$ | 300 | 70% – 80% |
| **Canada** | Passport | $50 \times 70\text{ mm}$ | 300 | 60% – 70% |
| **Australia** | Passport | $35 \times 45\text{ mm}$ | 300 | 70% – 80% |
| **Custom** | Any Document | User-defined mm & DPI | 300 | Automatic |

---

## 🛡️ License

This project is licensed under the **MIT License**.
