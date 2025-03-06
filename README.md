# Batting Order Optimization  
## Undergraduate Thesis Project  
  
### What's Happening Here?  
For my senior project, I am looking at the optimization of batting orders in the MLB in terms of runs produced (generally on a per game basis). This project was inspired by *The Book: Playing the Percentages in Baseball* in attempt to build and improve upon the conclusions about batting orders drawn there. The end goal of this project is to create a usable tool where a 9 man lineup, opposing SP, and league can be inputted and an optimal batting order given that situation will be returned.  
  
### So how is all of this done?  
A full explination can be found in the Final_Paper.pdf file (once it is finished and uploaded), however it boils down to a few basics.  
  1. Create a model that projects short term statistics for batters in BA, OBP, SLG, BB%, and K% (HR% was dropped due to it's volatility). 
  2. Create a model that adjusts those statistics from part 1 given the opposing SP. This is done at first using the Odds-Ratio Method, then adjusted given that the Odd-Ratio Method has some error.  
  3. Simulate, simulate, simulte. Over 2,000,000 games were simulated using OOTP 17 in order to establish two things: what is the relative impact of each spot in the batting order on runs produced *and* what is the relative impact of each statistic at each spot in the batting order on runs produced. A full table of the results can be found in the Final_Paper.pdf. 
  4. Combine everything above to choose an optimal lineup for any team, given they are a modern team (due to the changes in the run prodcution enviroment). The father back you go, the less reliable the results will be.  
  
### And what were the results?  
In short, the algorithm generates a statistically significant additional runs per game against bad to average pitching, but not against elite pitching. During backtesting, I tested the 2018 Dodgers and Mariners against Tyler Chatwood, Ivan Nova, Max Scherzer, and league average pitching. Against league average pitching, it generated an additional 0.06 runs per game (or 9.72 runs over a full season, about 1 additional win), and even more against below league average pitching. Against Ivan Nova and Max Scherzer, however, the difference in runs per game was not enough to be considered statistically significant (p < 0.05). 
