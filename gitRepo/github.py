import requests
from gitRepo.gitRepo import GitRepo
def _get_user_repos(user: str):
    res = requests.get('https://api.github.com/users/' + user + '/repos')
    repos = [x['clone_url'] for x in res.json()]
    while 'next' in res.links:
        res = requests.get(res.links['next']['url'])
        repos += [x['clone_url'] for x in res.json()]
    return repos

class GitHub:
    def __init__(self, repoman: GitRepo):
        self.repoman = repoman

    @staticmethod
    def get_user_repos(user: str):
        url = f'https://api.github.com/users/{user}/repos'
        while url:
            res = requests.get(url)
            res.raise_for_status()  # Optional but good practice to raise on bad responses
            for repo in res.json():
                yield repo['clone_url']
            url = res.links.get('next', {}).get('url')


    def mirror_repo(self, repo: str):
        return self.repoman.clone(repo, filter="github.com")

    def mirror_user_repos(self, user: str):
        for repo in self.get_user_repos(user):
            self.repoman.clone(repo, filter="github.com")