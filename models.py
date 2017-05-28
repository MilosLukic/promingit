import datetime

ALLOWED_FILE_TYPES = ['.py', '.html', '.js', '.css', '.rb']
ENFORCE_FILE_TYPES = True


class InvalidFileType(Exception):
    pass


class FileChange:
    def __init__(self, file, additions, deletions):
        self.file = file
        try:
            self.additions = int(additions)
            self.deletions = int(deletions)
        except ValueError:
            self.additions = 0
            self.deletions = 0
        self.changes = self.additions + self.deletions
        self.new_lines = self.additions - self.deletions
        if self.new_lines < 0:
            self.new_lines = 0


class File:
    def __init__(self, path):
        self.file_type = path[path.rfind('.'):-1]
        if ENFORCE_FILE_TYPES is True and self.file_type not in ALLOWED_FILE_TYPES:
            raise InvalidFileType
        self.path = path
        self.name = path[path.rfind('/')+1:]

    @property
    def is_test(self):
        return 'test' in self.name[:4] or 'spec.rb' in self.name


class Author:
    def __init__(self, author_email):
        self.author_email = author_email
        self.commits = []

    def __str__(self):
        return self.author_email


class Commit:
    def __init__(self, short_hash, author_time, commit_email, commit_time, branch):
        self.short_hash = short_hash
        self.author_time = datetime.datetime.fromtimestamp(float(author_time))
        self.commit_email = commit_email
        self.commit_time = datetime.datetime.fromtimestamp(float(commit_time))
        self.branch = branch
        self.comment = ''
        self.file_changes = []

    @property
    def number_of_changes(self):
        changes = 0
        for change in self.file_changes:
            changes += change.additions + change.deletions
        return changes

    @property
    def number_of_new_lines(self):
        new_lines = 0
        for change in self.file_changes:
            new_lines += change.new_lines
        return new_lines

    @property
    def number_of_deletions(self):
        deletions = 0
        for change in self.file_changes:
            deletions += change.deletions
        return deletions

    @property
    def number_of_test_new_lines(self):
        new_lines = 0
        for change in self.file_changes:
            if change.file.is_test:
                new_lines += change.new_lines
        return new_lines

    @property
    def is_merge_commit(self):
        return 'Merge branch' in self.comment

    def __str__(self):
        return "%s %s" % (self.short_hash, self.commit_time)