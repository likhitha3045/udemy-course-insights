# Deploy the dashboard

This project can be hosted on Streamlit Community Cloud. The deployed app starts with the included synthetic demo data. Upload a permitted `Course_info.csv` through the sidebar to analyze the real dataset. The uploaded file is supplied to the running app session; it is not saved as a permanent copy by this project.

## 1. Create a GitHub repository

1. Sign in to [GitHub](https://github.com/) and create a new repository.
2. Choose a repository name, such as `udemy-course-insights`. Choose public or private based on who should access the source. Do not add the source dataset to GitHub unless its terms allow redistribution.
3. From PowerShell, open this project folder (the folder containing `app.py`) and run:

   ```powershell
   git add .
   git commit -m "Prepare Udemy course dashboard"
   git branch -M main
   git remote set-url origin https://github.com/likhitha3045/udemy-course-insights.git
   git push -u origin main
   ```

   If the folder has not been initialized as a Git repository, run `git init` first. If it has no `origin` remote, use `git remote add origin https://github.com/likhitha3045/udemy-course-insights.git` instead of `git remote set-url`. The `.gitignore` excludes local CSV files in `data/` (except the synthetic demo sample) and virtual environments.

Do not commit the original course dataset unless its terms allow redistribution.

## 2. Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and grant access to the repository. You need admin access to deploy it.
2. Choose **Create app**, then select the repository, the `main` branch, and `app.py` as the app file.
3. Leave the Python version at the default or select a supported version, then choose **Deploy**.
4. When deployment completes, open the app URL. It should show the synthetic demo data. Upload a properly licensed dataset from the sidebar when you want to analyze it.

The repository includes `requirements.txt`, which Community Cloud uses to install the app dependencies. When you push future code changes to GitHub, Community Cloud redeploys the app from that repository.

For current deployment details, see [Streamlit's deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [GitHub connection guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account).
