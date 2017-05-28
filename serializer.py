class AuthorSerializer:
    fields = ['author', 'commit_number', 'all_new_lines', 'all_deleted_lines', 'commits_per_day',
              'files_per_commit', 'lines_per_commit', 'commits_under_25',
              'commits_above_500', 'test_line_ratio', 'merge_commits']

    def __init__(self, author):
        for field in self.fields:
            setattr(self, field, getattr(author, field, None))

    def print_author(self):
        print("{:<7}{:<15}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}".format(
            str(self.author),
            str(self.commit_number),
            self.all_new_lines,
            self.all_deleted_lines,
            self.commits_per_day,
            self.files_per_commit,
            self.lines_per_commit,
            self.commits_under_25,
            self.commits_above_500,
            self.test_line_ratio,
            self.merge_commits
        ))