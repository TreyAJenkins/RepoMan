from pydantic import BaseModel
from datetime import datetime
from git import Repo
from pathlib import Path
import json
import tqdm


class Metadata(BaseModel):
    date: datetime
    sha: str
    remote: str

    @classmethod
    def from_repo(cls, repo: Repo):
        commit = repo.commit()
        return cls(date=commit.committed_date, sha=commit.hexsha, remote=repo.remote().url)

    def to_dict(self):
        return json.loads(self.model_dump_json())

class Bundler:
    storage: Path
    datastore: dict

    def __init__(self, storage: Path = "./storage"):
        self.storage = storage
        self.datastore = {}

    def add_repo(self, path: Path):
        repo = Repo(path)
        metadata = Metadata.from_repo(repo).to_dict()
        self.datastore[str(path.relative_to(self.storage))] = metadata

    def add_all_repos(self):
        dirlist = list(Path("./storage").rglob("*/*.git"))
        for path in tqdm.tqdm(dirlist):
            try:
                self.add_repo(path)
            except ValueError:
                continue

