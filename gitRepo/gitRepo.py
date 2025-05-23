from git import Repo, GitCommandError
from pathlib import Path, PosixPath
from urlpath import URL
from git import RemoteProgress
from tqdm import tqdm
from dataclasses import dataclass
from gitRepo.dependencies import DepScanner
from colorama import Fore

class CloneProgress(RemoteProgress):
    def __init__(self, desc=None):
        super().__init__()
        self.pbar = tqdm(desc=desc)

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

class GitPath(PosixPath):
    def __new__(cls, url: str, root: Path = ""):
        if "@" in url:
            url = url.replace(":", '/').replace("@", "://")
        parsed = URL(url)
        host = parsed.hostname
        user = parsed.parts[1]
        repo = parsed.parts[2]
        if ".git" not in repo:
            repo = f"{repo}.git"

        return super().__new__(cls, root, host, user, repo)


class GitRepo:
    storage: Path
    repo: Repo

    def __init__(self, storage: Path):
        self.storage = storage


    def _clone(self, url: str, desc="MIRROR", filter:str=None, visited:list=None):
        destination = GitPath(url, self.storage)
        if str(destination) in visited:
            if destination.exists():
                return Repo(destination)
            return None
        repo = None
        if not destination.exists():
            try:
                repo = Repo.clone_from(url, to_path=GitPath(url, self.storage),
                                           progress=CloneProgress(desc=f"{desc}:{Fore.RESET} {GitPath(url)}"),
                                           multi_options=["--mirror"],
                                           env={
                                               "GIT_SSH_COMMAND": "ssh -o StrictHostKeyChecking=no",
                                               "GIT_TERMINAL_PROMPT" :"0"
                                           }
                                       )
                visited.append(str(destination))
            except GitCommandError as e:
                visited.append(str(destination))
                print(f"FAILED: {GitPath(url)} - {e.stderr}")
                return None
        else:
            #print(f"WARNING: Repository at {url} already exists!")
            repo = Repo(destination)
            repo.remotes.origin.fetch(progress=CloneProgress(desc=f"{Fore.YELLOW}UPDATE:{Fore.RESET} {GitPath(url)}"))
            visited.append(str(destination))
        deps = DepScanner(repo, filter=filter).submodules
        for dep in deps:
            self._clone(dep, desc=f"{Fore.GREEN}MODULE", filter=filter, visited=visited)
            visited.append(str(destination))
        return repo

    def clone(self, url: str, filter: str = None):
        return self._clone(url, desc=f"{Fore.LIGHTGREEN_EX}MIRROR", filter=filter, visited=[])
