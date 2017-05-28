from parser import Parser
from statistics import Statistics

parser = Parser('logs/project_gitlog.log')
data_container = parser.create_data_container()

# Create statistics
statistics = Statistics(data_container)
statistics.generate_statistics()
statistics.print_statistics()
#
serializer = statistics.general_serializer
json_data = serializer.serialize()

