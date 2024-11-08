# Job Trend Analyzer

## When Developing:

1. **Create a branch for your task**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/{jira-task-name}
2. **Do some coding/develop the feature**
3. **Commit/push feature**
   ```bash
   git commit -m "Description of changes"
   git push origin feature/{jira-task-name}
5. **Merge branch into main**
   ```bash
   git checkout main
   git pull origin main
   git merge feature/{jira-task-name}
6. **Resolve merge conflicts! If necessary**
7. **Push to main and delete feature branch**
   ```bash
   git push origin main
   git branch -d feature/{jira-task-name}

## To test locally:
1. cd job-trend-analyzer/backend/app
2. Run uvicorn api:app --reload (backend) in your command line
3. Open another terminal
4. cd job-trend-analyzer/dashboard-react-app
5. run npm start in your command line
