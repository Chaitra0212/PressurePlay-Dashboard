# PressurePlay Dashboard

## What this prototype does
- Displays the latest IPL and T20I Top 10 pressure batter/bowler rankings.
- Provides a Top 10 player explorer with pressure vs non-pressure metrics.
- Displays historical season-level pressure trends.
- Explains the pressure definition and methodology.

## Run locally (Windows)
1. Install Python 3.10 or newer.
2. Extract this folder.
3. Open Command Prompt in this folder.
4. Run:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If `py` is not recognized, try `python` instead.

The dashboard opens at `http://localhost:8501`.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Public access
Push this project folder to a GitHub repository, then deploy it through Streamlit Community Cloud:
- Create/sign in to GitHub and upload the project folder.
- Open https://share.streamlit.io/
- Choose the repository, branch, and `app.py`.
- Deploy.

Keep the `data/` folder in the repository. Do not upload private credentials or secrets.

## Scope note
This is an interactive dashboard using precomputed CSV outputs from the supplied notebooks. It does not yet accept a fresh ball-by-ball dataset and rerun the complete pressure calculations dynamically. That can be added as a later phase.
