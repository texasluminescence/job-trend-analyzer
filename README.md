# job-trend-analyzer

When developing:
1. Create a branch for your task
   git checkout main
   git pull origin main
   git checkout -b feature/{jira-task-name}
2. Do some coding/develop the feature
3. Commit/push feature
  git commit -m "Description of changes"
  git push origin feature/{jira-task-name}
4. Merge Branch into Main
  git checkout main
  git pull origin main
  git merge feature/{jira-task-name}
5. Resolve merge conflicts! If necessary
6. Push to main and delete feature branch
  git push origin main
  git branch -d feature/{jira-task-name}

To test locally:
1. cd job-trend-analyzer/backend/app
2. Run uvicorn api:app --reload (backend) in your command line
3. Open another terminal
4. cd job-trend-analyzer/dashboard-react-app
5. run npm start in your command line
