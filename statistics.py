import datetime

from models import Project
from serializer import AuthorSerializer, GeneralSerializer, ProjectSerializer


class ProjectPeriodStatistics:
    def __init__(self, data_container, statistics, time_from=None, time_to=None):
        self.data_container = data_container
        self.statistics = statistics
        self.project = Project(time_from, time_to)
        self.time_to = time_to
        self.time_from = time_from
        self.project_serializer = None
        self.extract_statistics()

    def extract_statistics(self):
        for key, author in self.statistics.authors.items():
            author_commits = self.filter_author_commits(author)
            if not author_commits:
                continue
            self.project.num_authors += 1
            self.project.commit_number += len(author_commits)
            self.project.all_new_lines += author.all_new_lines
            self.project.all_deleted_lines += author.all_deleted_lines
            self.project.commits_per_day += author.commits_per_day
            self.project.files_per_commit += author.files_per_commit
            self.project.commits_under_25 += author.commits_under_25
            self.project.commits_above_500 += author.commits_above_500
            self.project.test_line_number += author.test_line_number
            self.project.merge_commits += author.merge_commits

        self.project.files_per_commit = self.project.files_per_commit / float(self.project.num_authors)
        self.project.test_line_ratio = self.project.test_line_number / float(self.project.all_new_lines)
        self.project.lines_per_commit = self.project.all_new_lines / float(self.project.commit_number)
        self.project_serializer = ProjectSerializer(self.project)

    def filter_author_commits(self, author):
        if not self.time_from or not self.time_to:
            return author.commits
        author_commits = []
        if self.time_from and self.time_to:
            for commit in author.commits:
                if commit.commit_time > self.time_from and commit.commit_time < self.time_to:
                    author_commits.append(commit)
        return author_commits

    def print_project(self):
        print("{:<7}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}".format(
                'Author number', 'Commit number', 'New lines', 'Deleted lines', 'Commits/day', 'Files/commit', 'Lines/commit',
                'Commits < 25', 'Commits > 500',  'Test ratio', 'Merge Commits'
        ))
        self.project_serializer.print_project()

    def serialize_project_data(self):
        return self.project_serializer.get_dict(), \
               {'time_from': str(self.time_from), 'time_to': str(self.time_to)}

    def print_statistics(self):
        if self.time_from:
            print("Period %s - %s" % (str(self.time_from), str(self.time_to)))
        else:
            print('All time stats')
        self.print_project()
        print(" ")


class AuthorPeriodStatistics:
    def __init__(self, data_container, time_from=None, time_to=None):
        self.authors = data_container.author_dict
        self.files = data_container.file_dict
        self.commits_per_day = None
        self.obj_author_data = []
        self.time_from = time_from
        self.time_to = time_to
        self.extract_statistics()

    def extract_statistics(self):
        self.obj_author_data = []
        for key, author in self.authors.items():
            author_commits = self.filter_author_commits(author)
            if not author_commits:
                continue
            setattr(author, 'author', author.author_email)
            setattr(author, 'commit_number', len(author_commits))
            setattr(author, 'all_new_lines', self.get_all_new_lines(author_commits))
            setattr(author, 'all_deleted_lines', self.get_all_deleted_lines(author_commits))
            setattr(author, 'commits_per_day', self.get_commits_per_day(author_commits))
            setattr(author, 'files_per_commit', self.get_files_per_commit(author_commits))
            setattr(author, 'lines_per_commit', self.get_added_lines_per_commit(author))
            setattr(author, 'commits_under_25', self.get_commits_under(author_commits, 25))
            setattr(author, 'commits_above_500', self.get_commits_under(author_commits, 500))
            setattr(author, 'test_line_number', self.get_test_line_number(author_commits))
            setattr(author, 'test_line_ratio', self.get_test_line_ratio(author))
            setattr(author, 'merge_commits', self.get_all_merge_commits(author_commits))
            self.obj_author_data.append(AuthorSerializer(author))

    def filter_author_commits(self, author):
        if not self.time_from or not self.time_to:
            return author.commits
        author_commits = []
        if self.time_from and self.time_to:
            for commit in author.commits:
                if commit.commit_time > self.time_from and commit.commit_time < self.time_to:
                    author_commits.append(commit)
        return author_commits

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
        return valid_commits

    def get_all_new_lines(self, commits):
        return sum([commit.number_of_new_lines for commit in commits])

    def get_all_deleted_lines(self, commits):
        return sum([commit.number_of_deletions for commit in commits])

    def get_all_changed_lines(self, commits):
        return sum([commit.number_of_changes for commit in commits])

    def get_all_merge_commits(self, commits):
        return len([commit for commit in commits if commit.is_merge_commit])

    def get_test_line_number(self, commits):
        test_lines = sum([commit.number_of_test_new_lines for commit in commits])
        return test_lines

    def get_test_line_ratio(self, author):
        if author.test_line_number == 0:
            return 0
        return author.test_line_number/author.all_new_lines

    def get_added_lines_per_commit(self, author):
        return author.all_new_lines / len(author.commits)


    def print_authors(self):
        print("{:<7}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}".format(
                'Author', 'Commit number', 'New lines', 'Deleted lines', 'Commits/day', 'Files/commit', 'Lines/commit',
                'Commits < 25', 'Commits > 500',  'Test ratio', 'Merge Commits'
        ))
        for serialized_author in self.obj_author_data:
            serialized_author.print_author()

    def serialize_author_data(self):
        return [author_obj.get_dict() for author_obj in self.obj_author_data], \
               {'time_from': str(self.time_from), 'time_to': str(self.time_to)}

    def print_statistics(self):
        if self.time_from:
            print("Period %s - %s" % (str(self.time_from), str(self.time_to)))
        else:
            print('All time stats')
        self.print_authors()
        print(" ")


class Statistics:
    def __init__(self, data_container):
        self.general_serializer = GeneralSerializer()
        self.data_container = data_container
        self.quartal_statistics = []
        self.quartal_project_statistics = []
        self.all_time_stats = None

    def generate_statistics(self):
        self.all_time_stats = self.generate_all_time_stats()
        self.all_time_project_stats = self.generate_all_time_project_stats()
        self.generate_quartal_statistics()

    def generate_all_time_stats(self):
        statistics = AuthorPeriodStatistics(self.data_container)
        self.general_serializer.insert(*statistics.serialize_author_data())
        return statistics

    def generate_all_time_project_stats(self):
        statistics = ProjectPeriodStatistics(self.data_container, self.all_time_stats)
        self.general_serializer.insert(*statistics.serialize_project_data())
        return statistics

    def generate_quartal_statistics(self):
        start_date, end_date = self.get_project_interval()
        quartal = datetime.timedelta(days=90)
        while start_date < end_date:
            stats = AuthorPeriodStatistics(self.data_container, time_from=start_date, time_to=start_date + quartal)
            project_stats = ProjectPeriodStatistics(self.data_container, stats, time_from=start_date, time_to=start_date + quartal)
            start_date += quartal
            self.quartal_statistics.append(stats)
            self.quartal_project_statistics.append(project_stats)
            self.general_serializer.insert(*stats.serialize_author_data())
            self.general_serializer.insert(*project_stats.serialize_project_data())

    def print_statistics(self, all=False):
        if all:
            self.all_time_stats.print_statistics()
            for statistics in self.quartal_statistics:
                statistics.print_statistics()

        self.all_time_project_stats.print_statistics()
        for statistics in self.quartal_project_statistics:
            statistics.print_statistics()

    def get_project_interval(self):
        return self.data_container.commit_list[-1].commit_time, self.data_container.commit_list[0].commit_time