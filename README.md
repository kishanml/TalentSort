# TalentSort

**TalentSort** helps HR professionals identify top talent from a pool of qualified candidates using AI.  
It’s a very basic demonstration of candidate evaluation using **Gemini API** that automates early-stage recruitment tasks—comparing resumes to job descriptions, scoring candidates, analyzing profile details, and generating customized interview questions.

---

## How It Works

1. **Upload a Resume**
2. **Provide a Job Description**
3. **TalentSort**:
   - Scores the candidate
   - Extracts key insights
   - Generates relevant interview questions
4. **HR Team** uses the output for the first round of interviews—no technical team needed.

---


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/tal
```

### 2. Add Your Gemini API Key

Create a .env file in the root directory and add:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies

We recommend using a virtual environment:

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

## Preview


<img width="1900" height="1051" alt="Screenshot from 2025-10-17 15-07-14" src="https://github.com/user-attachments/assets/1e9cf2b9-c283-428a-a902-22d2840de879" />


