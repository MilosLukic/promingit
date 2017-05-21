from random import randint

import datetime

ALLOWED_FILE_TYPES = ['.py', '.html', '.js', '.css', '.rb']
ENFORCE_FILE_TYPES = False


class InvalidFileType(Exception):
    pass


class Helpers:
    @staticmethod
    def scramble_function(email):
        return email[:3] + email[-3:]


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
            try:
                self.files[file_path] = File(file_path)
            except InvalidFileType:
                return

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

    def is_start(self, line):
        return line[:5] == 'start'

    def is_end(self, line):
        return line[:3] == 'end'

    def is_startcomment(self, line):
        return line[:12] == 'startcomment'


class Statistics:
    def __init__(self, authors, files):
        self.authors = authors
        self.files = files
        self.commits_per_day = None

    def extract_statistics(self):
        for key, author in self.authors.items():
            setattr(author, 'commits_per_day', self.get_commits_per_day(author.commits))
            setattr(author, 'files_per_commit', self.get_files_per_commit(author.commits))
            setattr(author, 'commits_under_50', self.get_commits_under(author.commits, 25))
            setattr(author, 'commits_under_500', self.get_commits_under(author.commits, 250))
            setattr(author, 'all_new_lines', self.get_all_new_lines(author.commits))
            setattr(author, 'test_line_ratio', self.get_test_line_ratio(author.commits))
            setattr(author, 'merge_commits', self.get_all_merge_commits(author.commits))

    def get_commits_per_day(self, commits):
        day_averages = [0]
        current_time = commits[0].author_time
        DAY_THRESHOLD = 8
        current_day_span = datetime.timedelta(hours=0)

        for commit in commits:
            if commit.author_time > current_time - datetime.timedelta(hours=DAY_THRESHOLD) and current_day_span < datetime.timedelta(hours=18):
                day_averages[-1] += 1
                current_day_span = current_time - commit.author_time
            else:
                day_averages.append(1)
                current_day_span = datetime.timedelta(hours=0)
            current_time = commit.author_time
        return sum(day_averages)/len(day_averages)

    def get_files_per_commit(self, commits):
        sum_files = []
        for commit in commits:
            sum_files.append(len(commit.file_changes))
        return sum(sum_files)/len(commits)

    def get_commits_under(self, commits, number_of_lines):
        valid_commits = 0
        for commit in commits:
            if commit.number_of_changes < number_of_lines:
                valid_commits += 1
        return valid_commits/len(commits)

    def get_all_new_lines(self, commits):
        return sum([commit.number_of_new_lines for commit in commits])

    def get_all_merge_commits(self, commits):
        return len([commit for commit in commits if commit.is_merge_commit])

    def get_test_line_ratio(self, commits):
        return sum([commit.number_of_test_new_lines for commit in commits])/self.get_all_new_lines(commits)

    def print_authors(self):
        print("{:<7}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}".format(
                'Author', 'Commit number', 'Commits/day', 'Files/commit',
                'Commits < 25', 'Commits < 250', 'New lines', 'Test line ratio', 'Merge Commits'
        ))
        for key, author in self.authors.items():
            print("{:<7}{:<15}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15}{:<15.2f}{:<15}".format(
                    str(author),
                    str(len(author.commits)),
                    author.commits_per_day,
                    author.files_per_commit,
                    author.commits_under_50,
                    author.commits_under_500,
                    author.all_new_lines,
                    author.test_line_ratio,
                    author.merge_commits
            ))


parser = Parser('logs/project_gitlog.log')
statistics = Statistics(parser.authors, parser.files)
statistics.extract_statistics()
statistics.print_authors()