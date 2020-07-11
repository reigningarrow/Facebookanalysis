# Facebookanalysis
A simple python code to scrape your facebook friend data to get a network graph

These are two pieces of code to allow you to analyse your network for mutal friends.
The first (facebook scraper) requires you to have the chromedriver in the same folder as it and opens a new instance of chrome and logs into your Facebook and starts getting the data. This will take a while as it has to pause regularly to stop getting locked out for unusual activity. It then saves this data to a pickle file which can then be accessed by the second script. This also creates a file to be used directly in GEPHI if you don't want to use the second Python Script.

The second file takes the pickled data and analyses it to produce several graphs using Networkx. This also removes the users node on the graph and then saves this modified data to be used in GEPHI if needed.
