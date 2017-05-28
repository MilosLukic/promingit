import matplotlib.pyplot as plt
import numpy
print(numpy.__path__)
from serializer import ProjectSerializer


class Visualisation:
    def __init__(self, statistics):
        serializer = statistics.all_time_project_stats.project_serializer
        quartal_serializers = [st.project_serializer for st in statistics.quartal_project_statistics]
        for field in ProjectSerializer.fields:
            plt.plot([st.time_from for st in statistics.quartal_project_statistics], [getattr(s, field) for s in quartal_serializers])
            plt.tick_params(axis='both', which='major', labelsize=8)
            plt.tick_params(axis='both', which='minor', labelsize=6)
            plt.savefig('images/%s.png' % field)
            plt.close()
