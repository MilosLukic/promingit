import datetime


class Statistics:
    def __init__(self, data_container):
        self.authors = data_container.author_dict
        self.files = data_container.file_dict
        self.commits_per_day = None

    def extract_statistics(self):
        for key, author in self.authors.items():
            setattr(author, 'all_new_lines', self.get_all_new_lines(author.commits))
            setattr(author, 'all_deleted_lines', self.get_all_deleted_lines(author.commits))
            setattr(author, 'commits_per_day', self.get_commits_per_day(author.commits))
            setattr(author, 'files_per_commit', self.get_files_per_commit(author.commits))
            setattr(author, 'lines_per_commit', self.get_added_lines_per_commit(author))
            setattr(author, 'commits_under_25', self.get_commits_under(author.commits, 25))
            setattr(author, 'commits_above_500', self.get_commits_under(author.commits, 500))
            setattr(author, 'test_line_ratio', self.get_test_line_ratio(author.commits))
            setattr(author, 'merge_commits', self.get_all_merge_commits(author.commits))

    def per_author_statistics(self):
        # TODO: Create one loop for all statistics
        #for key, author in self.authors.items():
        #    self.extract_author_statistics(author)
        pass

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

    def get_all_deleted_lines(self, commits):
        return sum([commit.number_of_deletions for commit in commits])

    def get_all_changed_lines(self, commits):
        return sum([commit.number_of_changes for commit in commits])

    def get_all_merge_commits(self, commits):
        return len([commit for commit in commits if commit.is_merge_commit])

    def get_test_line_ratio(self, commits):
        return sum([commit.number_of_test_new_lines for commit in commits])/self.get_all_new_lines(commits)

    def get_added_lines_per_commit(self, author):
        return author.all_new_lines / len(author.commits)


    def print_authors(self):
        print("{:<7}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}".format(
                'Author', 'Commit number', 'New lines', 'Deleted lines', 'Commits/day', 'Files/commit', 'Lines/commit',
                'Commits < 25', 'Commits > 500',  'Test ratio', 'Merge Commits'
        ))
        for key, author in self.authors.items():
            print("{:<7}{:<15}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}".format(
                    str(author),
                    str(len(author.commits)),
                    author.all_new_lines,
                    author.all_deleted_lines,
                    author.commits_per_day,
                    author.files_per_commit,
                    author.lines_per_commit,
                    author.commits_under_25,
                    author.commits_above_500,
                    author.test_line_ratio,
                    author.merge_commits
            ))

