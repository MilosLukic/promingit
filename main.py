from random import randint


class Helpers:
    @staticmethod
    def scramble_function(email):
        return email[:3] + email[-3:]


class FileChange:
    def __init__(self, file, additions, deletions):
        self.file = file
        self.additions = additions
        self.deletions = deletions


class File:
    def __init__(self, path):
        self.path = path
        self.name = path[path.rfind('/')+1:]


class Author:
    def __init__(self, author_email):
        self.author_email = author_email
        self.commits = []

    def __str__(self):
        return self.author_email

class Commit:
    def __init__(self, short_hash, author_time, commit_email, commit_time, branch):
        self.short_hash = short_hash
        self.author_time = author_time
        self.commit_email = commit_email
        self.commit_time = commit_time
        self.branch = branch
        self.comment = ''
        self.file_changes = []

    def __str__(self):
        return "%s %s" % (self.short_hash, self.commit_time)

class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.summary_start = False
        self.comment_start = False
        self.authors = {}
        self.files = {}
        self.current_author = None
        self.open_file()

    def open_file(self):
        with open(self.file_path, 'r') as file:
            self.read_cycle(file)

    def read_cycle(self, file):
        lines = file.readlines()
        for line in lines:
            self.process_line(line)

    def process_line(self, line):
        if len(line) <= 1:
            return

        if not self.summary_start and self.is_start(line):
            self.summary_start = True
        elif self.summary_start and self.is_startcomment(line):
            self.summary_start = False
            self.comment_start = True
        elif self.comment_start and self.is_end(line):
            self.comment_start = False
        elif self.comment_start:
            self.init_comment(line)
        elif self.summary_start:
            self.init_commit_from_summary(line)
        else:
            self.init_file_change(line)

    def init_commit_from_summary(self, line):
        commit_parameters, author_parameters = self.map_parameters(line)

        commit = Commit(**commit_parameters)

        if not author_parameters['author_email'] in self.authors:
            author = Author(**author_parameters)
            self.authors[author.author_email] = author
        self.current_author = self.authors[author_parameters['author_email']]
        self.current_author.commits.append(commit)

    def init_comment(self, line):
        self.current_author.commits[-1].comment += "%s " % line

    def init_file_change(self, line):
        parameters = line.split('\t')
        additions, deletions, file_path = parameters

        if not file_path in self.files:
            self.files[file_path] = File(file_path)

        file = self.files[file_path]
        file_change = FileChange(file, additions, deletions)
        self.current_author.commits[-1].file_changes.append(file_change)

    def map_parameters(self, line):
        params = line.split(';')[:6]
        author_parameters = {
            'author_email': Helpers.scramble_function(params[1])
        }
        commit_parameters = {
            'short_hash': params[0],
            'author_time': params[2],
            'commit_email': Helpers.scramble_function(params[3]),
            'commit_time': params[4],
            'branch': params[5],
        }
        return commit_parameters, author_parameters

    def print_authors(self):
        print("{:<7}{:<51}".format('Author', 'Commit number'))
        for key, author in self.authors.items():
            print("{:<10}{:<10}".format(str(author), str(len(author.commits))))

    def is_start(self, line):
        return line[:5] == 'start'

    def is_end(self, line):
        return line[:3] == 'end'

    def is_startcomment(self, line):
        return line[:12] == 'startcomment'

parser = Parser('logs/project_gitlog.log')
parser.print_authors()