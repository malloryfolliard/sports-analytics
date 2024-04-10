# This script scrapes the partial URL of every box
# score in the team schedule and then reconstructs
# the full URL. The idea is that you could then go
# to each of these box score URLs and scrape further
# data.

import requests, re, math
from bs4 import BeautifulSoup
from datetime import datetime


# Site to begin scraping
url = "https://www.pro-football-reference.com/teams/nwe/"

# Scrape start page into tree
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# Isolate the schedule table by id, and grab every row
schedule_table = soup.find(id="all_team_index")
rows = schedule_table.findChildren('tr')

Wins = 0; 
nightGame = 0;
nightWin = 0; 
totalGames = 0; 
fiveSeasons = 0; 

schedule_table = soup.find(id="all_team_index")
if schedule_table:
    rows = schedule_table.find_all('tr')

    fiveSeasons = 0
    last_season = None

    # Loop through every row
    for row in rows:
        season_url = row.find('th', {"data-stat": "year_id"})
        

        # Check if it's a new season
        if season_url and season_url.text != last_season:
            fiveSeasons += 1
            last_season = season_url.text

        if fiveSeasons > 6:
            break

        game_href = None
        if season_url:
            season_link = season_url.find('a', href=True)
            if season_link:
                game_href = season_link['href']

                # Get the root url of the page variable
                regex = r'.*\.com'
                url_root = re.findall(regex, url)[0]
                
                # Formulate the final game base_url
                game_url = '{}{}'.format(url_root, game_href)

                # Scrape each game page
                page2 = requests.get(game_url)
                soup2 = BeautifulSoup(page2.content, "html.parser")


                # Isolate the schedule table by id, and grab every row
                schedule_table2 = soup2.find(id="games")
                if schedule_table2:
                    rows2 = schedule_table2.find_all('tr')
                    for row2 in rows2:
                        # Isolate the box score cell using the data-stat attribute
                        outcome = row2.find('td', {"data-stat": "game_outcome"})
                        game_times = row2.find('td', {"data-stat": "game_time"})

                        totalGames += 1 

                        if game_times:
                            try:
                                # Remove the timezone from the time string for parsing
                                game_time_str = game_times.text.strip().rsplit(' ', 1)[0]
                                if len(game_time_str) == 0:
                                    continue
                                game_time_obj = datetime.strptime(game_time_str, '%I:%M%p').time()

                                # Convert the comparison time to a datetime.time object
                                comparison_time_obj = datetime.strptime("5:30PM", '%I:%M%p').time()

                                if game_time_obj > comparison_time_obj:
                                    nightGame += 1
                                    if outcome and outcome.text.strip() == 'W':
                                        nightWin += 1
                                        Wins += 1; 
                                elif outcome and outcome.text.strip() == 'W':
                                    Wins += 1   

                            except ValueError as e:
                                print(f"Error parsing time: {e}")
          
                        else:
                            continue


# print("nightgames ", nightGame)
# print("wins: ", Wins)
# print("total games", totalGames)
if totalGames > 0:
    # probA = prob of a next game being a night game from 5 seasons of data
    probA = nightGame / totalGames
    # probB = prob of a win in the next game from 5 seasons of data
    probB = Wins / totalGames

    probBandA = nightWin / totalGames

    if nightGame > 0:
        # prob of a win based on in the next game given its a night game 
        probBgivenA = probBandA / probA
        if probB > 0:
            probAgivenB = (probBgivenA * probA) / probB
            print(f"Probability (P(A|B)): {probAgivenB:.10f}") 

        
