from data_container import DataContainer
from models import Commit, Author, File, FileChange, InvalidFileType


class Helpers:
    @staticmethod
    def scramble_function(email):
        return email[:3] + email[-3:]


class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.summary_start = False
        self.comment_start = False
        self.author_dict = {}
        self.file_dict = {}
        self.file_list = []
        self.file_change_list = []
        self.author_list = []
        self.commit_list = []
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
        self.commit_list.append(commit)

        if not author_parameters['author_email'] in self.author_dict:
            author = Author(**author_parameters)
            self.author_list.append(author)
            self.author_dict[author.author_email] = author
        self.current_author = self.author_dict[author_parameters['author_email']]
        self.current_author.commits.append(commit)

    def init_comment(self, line):
        self.current_author.commits[-1].comment += "%s " % line

    def init_file_change(self, line):
        parameters = line.split('\t')
        additions, deletions, file_path = parameters

        if not file_path in self.file_dict:
            try:
                file = File(file_path)
                self.file_dict[file_path] = file
                self.file_list.append(file)
            except InvalidFileType:
                return

        file = self.file_dict[file_path]

        file_change = FileChange(file, additions, deletions)
        self.file_change_list.append(file_change)

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

    def create_data_container(self):
        return DataContainer(
            author_list=self.author_list,
            author_dict=self.author_dict,
            commit_list=self.commit_list,
            file_list=self.file_list,
            file_dict=self.file_dict,
            file_change_list=self.file_change_list
        )

