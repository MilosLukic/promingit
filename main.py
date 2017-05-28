from parser import Parser
from statistics import Statistics

parser = Parser('logs/project_gitlog.log')
data_container = parser.create_data_container()
statistics = Statistics(data_container)
serialized_statistics = statistics.generate_statistics()