# GitHub and Streamlit Community Cloud

Repository: https://github.com/benjaminj23/sydneytransitbench-dashboard

## Deploy

1. Sign in at https://share.streamlit.io using GitHub.
2. Choose **Create app**, then deploy an app from GitHub.
3. Select repository `benjaminj23/sydneytransitbench-dashboard`, branch `main`, main file `app.py`.
4. In advanced settings choose Python **3.11** (the tested version).
5. Deploy and wait for installation to finish. The app starts in demo mode.

`requirements.txt` and `.streamlit/config.toml` are already included. No secrets are required. Updates committed to the selected GitHub branch are picked up by Community Cloud.

## Local launch

From the repository root, after installing dependencies:

```powershell
python -m streamlit run app.py
```

Never commit `.streamlit/secrets.toml`, `.env` files, credentials or unapproved research datasets. Local Windows dataset paths will not exist on Community Cloud; hosted deployments need files available within the hosted environment and approved for its audience. See INTEGRATION.md before attaching real data.
