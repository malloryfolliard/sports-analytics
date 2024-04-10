import csv
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
# Feel free to add anything else you need here
import pandas as pd
import math


# read in play by play data as data frame
events = pd.read_csv('0021500495.csv', index_col=None)
events = events.iloc[1:, :]


# Read in the SportVU tracking data
sportvu = []
with open('0021500495.json', mode='r') as sportvu_json:  
    sportvu = json.load(sportvu_json)
# Convert SportVU data to DataFrame for easier manipulation
sportvu_df = pd.DataFrame(sportvu['events'])

data = pd.DataFrame.from_dict(sportvu)
data['event_id'] = data['events'].apply(lambda x: int(x['eventId']))

# filter and merge data sources to only focus on shot events
shot_df = events[events['EVENTMSGTYPE'].isin([1, 2])]
data = data[data['event_id'].isin(list(shot_df['EVENTNUM']))].reset_index(drop=True)
shot_df = shot_df.reset_index(drop=True)
shot_df['events'] = data['events']

# function to scale data
def scale_to_10(values):
    min_val = min(values)
    max_val = max(values)
    scaled_values = [(x - min_val) / (max_val - min_val) * 10 for x in values]
    return scaled_values


# Hypothetical function to extract shot times and a simple fact (e.g., attempt number)
def extract_shot_data(sportvu_data):
    shot_times = []
    temp_moments = []
    shot_facts = []
    last_recorded_shot = 912
    # Iterate through events to find shots 
    for event in sportvu_data['events']:
        for moment in event['moments']:

            temp_moments.append(moment)

            ball = ((moment[5][0][0] == -1) and (moment[5][0][1] == -1))
            aboveHoop = moment[5][0][4] > 10
            xlocRim = (moment[5][0][3] > 24) and (moment[5][0][3] < 26)
            ylocRim = ((moment[5][0][2] > 4) and (moment[5][0][2] < 6)) or ((moment[5][0][2] > 88) and (moment[5][0][2] < 90))
            
            # above and near hoop
            if (ball and aboveHoop and xlocRim and ylocRim):
                
                # see if within 5 seconds of last recorded shot
                if((last_recorded_shot - moment[2]) > 5): 
                    last_recorded_shot = moment[2]
                
                # looping backwards through moments to find shooter
                for blah in reversed(temp_moments):
                    # ball under 8 feet, assume we are at the shooter
                    if (blah[5][0][4] < 8):
                        #calculate time since start
                        timeElapsed = ((blah[0] - 1) * 720) + (720 - blah[2])
                        #check that this shot has not already been added
                        add = True
                        for times in shot_times:
                            if (times == timeElapsed):
                                add = False
                        # if not already added, then add
                        if add:
                            # add shot time

                            shot_times.append(timeElapsed)
                            # find player closest to ball(shooter) in this moment
                            xDiff = abs(blah[5][0][2] - blah[5][1][2])
                            yDiff = abs(blah[5][0][3] - blah[5][1][3])
                            shooter = blah[5][1]
                            for p in blah[5]:
                                if p[0] != -1:
                                    # print ("this is p: ", p)
                                    if xDiff > abs(blah[5][0][2] - p[2]):
                                        if yDiff > abs(blah[5][0][3] - p[3]):
                                            shooter = p
                            
                            # print("this is the shooter: ", shooter)

                            playerCoords = [shooter[2], shooter[3]]
                            closeHoopCoords = [5, 25]
                            farHoopCoords = [89, 25]
                            # This assumes they are not shooting half court shots
                            # add distance to array, based on which hoops shooting at
                            if shooter[2] < 45:
                                # print("Shot distance(close): ", math.dist(closeHoopCoords,playerCoords))
                                shot_facts.append(math.dist(closeHoopCoords,playerCoords))
                            else:
                                # print("Shot distance(far): ", math.dist(farHoopCoords,playerCoords))
                                shot_facts.append(math.dist(farHoopCoords,playerCoords))
                        break

                temp_moments = []
                    
                    
    # for times in shot_times:
    #     print("TIMES: ", times)
    
    shot_facts = scale_to_10(shot_facts)
    # for facts in shot_facts:
    #     print("FACTS: ", facts)

                
    return np.array(shot_times), np.array(shot_facts)


    


# Use the function to populate the arrays
shot_times, shot_facts = extract_shot_data(sportvu)




# YOUR SOLUTION GOES HERE


# These are the two arrays that you need to populate with actual data
# shot_times = np.array([30, 705, 1870, 2500]) # Between 0 and 2880
# shot_facts = np.array([5, 10, 8, 2]) # Scaled between 0 and 10




# This code creates the timeline display from the shot_times
# and shot_facts arrays.
# DO NOT MODIFY THIS CODE APART FROM THE SHOT FACT LABEL
fig, ax = plt.subplots(figsize=(12,3))
fig.canvas.manager.set_window_title('Shot Timeline')


plt.scatter(shot_times, np.full_like(shot_times, 0), marker='o', s=50, color='royalblue', edgecolors='black', zorder=3, label='shot')
plt.bar(shot_times, shot_facts, bottom=2, color='royalblue', edgecolor='black', width=5, label='shot fact') # <- This is the label you can modify

ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.tick_params(axis='x', length=20)
ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0,720,1440,2160,2880])) 
ax.set_yticks([])

_, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()
ax.set_xlim(-15, xmax)
ax.set_ylim(ymin, ymax+5)
ax.text(xmax, 2, "time", ha='right', va='top', size=10)
plt.legend(ncol=5, loc='upper left')

plt.tight_layout()
plt.show()

#plt.savefig("Shot_Timeline.png")
