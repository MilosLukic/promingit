from parser import Parser
from statistics import Statistics
from visualisation import Visualisation

parser = Parser('logs/project_gitlog.log')
data_container = parser.create_data_container()

# Serailize data for

# Create statistics
statistics = Statistics(data_container)
statistics.generate_statistics()
statistics.print_statistics()
visualisation = Visualisation(statistics)
#
serializer = statistics.general_serializer
json_data = serializer.serialize()

