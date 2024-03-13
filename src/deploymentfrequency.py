from github import Github
import datetime
import os

class DeploymentFrequency:
    def __init__(self, owner_repo, workflows, branch, number_of_days, pat_token=""):
        self.owner_repo = owner_repo
        self.workflows = workflows.split(',')
        self.branch = branch
        self.number_of_days = number_of_days
        self.pat_token = pat_token
        self.github = Github(pat_token) if pat_token else Github()
        self.owner, self.repo_name = owner_repo.split('/')
        self.repo = self.github.get_repo(f"{self.owner}/{self.repo_name}")

    def fetch_workflow_runs(self):
        workflow_runs_list = []
        unique_dates = set()

        for workflow_name in self.workflows:
            workflows = self.repo.get_workflows()
            for workflow in workflows:
                if workflow.name == workflow_name:
                    runs = workflow.get_runs(branch=self.branch)
                    for run in runs:
                        run_date = run.created_at
                        if run_date > datetime.datetime.now() - datetime.timedelta(days=self.number_of_days):
                            workflow_runs_list.append(run)
                            unique_dates.add(run_date.date())
        
        return workflow_runs_list, unique_dates

    def calculate_deployments_per_day(self, workflow_runs_list):
        if self.number_of_days > 0:
            return len(workflow_runs_list) / self.number_of_days
        return 0

    def report(self):
        workflow_runs_list, unique_dates = self.fetch_workflow_runs()
        deployments_per_day = self.calculate_deployments_per_day(workflow_runs_list)

        print(f"Owner/Repo: {self.owner}/{self.repo_name}")
        print(f"Workflows: {', '.join(self.workflows)}")
        print(f"Branch: {self.branch}")
        print(f"Number of days: {self.number_of_days}")
        print(f"Deployment frequency over the last {self.number_of_days} days is {deployments_per_day} per day")

if __name__ == "__main__":
    owner_repo = os.getenv('REPOSITORY')
    token = os.getenv('GITHUB_TOKEN')  # Your personal access token or GitHub App token
    workflows = 'Apply release,Release framework,Sonarcloud scan integrations'
    branch = 'main'
    time_frame = int(os.getenv('TIMEFRAME_IN_DAYS'))
    number_of_days = 30 if not time_frame else time_frame
    
    df = DeploymentFrequency(owner_repo,workflows, branch, number_of_days, pat_token=token)
    df.report()
