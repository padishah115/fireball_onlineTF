####################################################################
# TEMPORARY FILE FOR PLAYING AROUND WITH PLOTTING THE SCOPE TRACES #
####################################################################

#MODULE IMPORTS
import matplotlib.pyplot as plt
import pandas as pd

data_path = './example_data/C1--XX_SCOPE2--00081.CSV'

def plot_trace():

    scope_data = pd.read_csv(data_path)
    t = scope_data['Time']
    v = scope_data['Ampl']

    print(v)

    plt.plot(t, v)
    plt.show()

plot_trace()