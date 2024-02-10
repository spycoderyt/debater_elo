# %%
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os

# Replace 'path/to/your/webdriver' with the path to the WebDriver you're using (e.g., chromedriver)
from cli_args_system import Args

# for dont try to convert the host
args = Args(convert_numbers=False)

website_url = args.flag_str("w", "web", "website")
isolated = args.flag_str("i", "isolated")
if isolated != 1:
    isolated = False
print(f"doing for {website_url}")

DRIVER_BIN = "/chromedriver"
options = webdriver.ChromeOptions()
service = Service()
target_folder = os.path.join(os.getcwd(), "downloads")
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": target_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    },
)
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)


# %%

# Go to the PowerSchool login page
driver.get(website_url)
# Wait for the page to load completely
time.sleep(5)

h6_elements = driver.find_elements(
    By.CSS_SELECTOR, "div.popover-header.d-flex h6.flex-grow-1"
)

span_content = driver.find_elements(
    By.CSS_SELECTOR, "div.popover-body div.list-group-item span"
)

# %%
element_list = [element.get_attribute("innerHTML") for element in h6_elements]
teammate_list = [
    element.get_attribute("innerHTML")
    for element in span_content
    if not element.get_attribute("innerHTML").startswith("Total")
]

# %%
school_history = dict()
teams = dict()


# %%
def remove_prefix(str, prefix):
    return str.lstrip(prefix)


# %%
cur = ""
idx = 0
for txt in element_list:

    if txt.startswith("Won") or txt.startswith("Lost"):
        name = remove_prefix(txt, "Won against ")
        name = remove_prefix(name, "Lost against ")
    else:
        name = txt
    teams[name] = teammate_list[idx].split(", ")
    idx += 1
    if not txt.startswith("Won") and not txt.startswith("Lost"):
        cur = txt
        school_history[cur] = []
    else:
        school_history[cur].append(txt)


# %%
print(school_history)

# %%
for i in teams:
    print(i, teams[i])

# %%
driver.quit()


# %%


class Implementation:
    """
    A class that represents an implementation of the Elo Rating System
    """

    def __init__(self, base_rating=1000):
        """
        Runs at initialization of class object.
        @param base_rating - The rating a new player would have
        """
        self.base_rating = base_rating
        self.players = []

    def __getPlayerList(self):
        """
        Returns this implementation's player list.
        @return - the list of all player objects in the implementation.
        """
        return self.players

    def getPlayer(self, name):
        """
        Returns the player in the implementation with the given name.
        @param name - name of the player to return.
        @return - the player with the given name.
        """
        for player in self.players:
            if player.name == name:
                return player
        return None

    def contains(self, name):
        """
        Returns true if this object contains a player with the given name.
        Otherwise returns false.
        @param name - name to check for.
        """
        for player in self.players:
            if player.name == name:
                return True
        return False

    def applyUpdates(self):
        for player in self.players:
            player.rating += player.updates
            player.updates = 0

    def addPlayer(self, name, rating=None):
        """
        Adds a new player to the implementation.
        @param name - The name to identify a specific player.
        @param rating - The player's rating.
        """
        if rating == None:
            rating = self.base_rating

        self.players.append(_Player(name=name, rating=rating))

    def removePlayer(self, name):
        """
        Adds a new player to the implementation.
        @param name - The name to identify a specific player.
        """
        self.__getPlayerList().remove(self.getPlayer(name))

    def recordMatch(self, name1, name2, winner=None, draw=False):
        """
        Should be called after a game is played.
        @param name1 - name of the first player.
        @param name2 - name of the second player.
        """
        player1 = self.getPlayer(name1)
        player2 = self.getPlayer(name2)

        expected1 = player1.compareRating(player2)
        expected2 = player2.compareRating(player1)

        k = 16

        rating1 = player1.rating
        rating2 = player2.rating

        if draw:
            score1 = 0.5
            score2 = 0.5
        elif winner == name1:
            score1 = 1.0
            score2 = 0.0
        elif winner == name2:
            score1 = 0.0
            score2 = 1.0
        else:
            raise InputError("One of the names must be the winner or draw must be True")

        newRating1 = rating1 + k * (score1 - expected1)
        newRating2 = rating2 + k * (score2 - expected2)

        if newRating1 < 0:
            newRating1 = 0
            newRating2 = rating2 - rating1

        elif newRating2 < 0:
            newRating2 = 0
            newRating1 = rating1 - rating2

        player1.updates += newRating1 - rating1
        player2.updates += newRating2 - rating2
        # return rating1, score1, expected1, rating2, score2, expected2

    def getPlayerRating(self, name):
        """
        Returns the rating of the player with the given name.
        @param name - name of the player.
        @return - the rating of the player with the given name.
        """
        player = self.getPlayer(name)
        return player.rating

    def getRatingList(self):
        """
        Returns a list of tuples in the form of ({name},{rating})
        @return - the list of tuples
        """
        lst = []
        for player in self.__getPlayerList():
            lst.append((player.name, player.rating))
        return lst


class _Player:
    """
    A class to represent a player in the Elo Rating System
    """

    def __init__(self, name, rating):
        """
        Runs at initialization of class object.
        @param name - TODO
        @param rating - TODO
        """
        self.name = name
        self.rating = rating
        self.updates = 0

    def compareRating(self, opponent):
        """
        Compares the two ratings of the this player and the opponent.
        @param opponent - the player to compare against.
        @returns - The expected score between the two players.
        """
        return (1 + 10 ** ((opponent.rating - self.rating) / 400.0)) ** -1


# %%
# start with school_history which has list of teams and matchups
# teammate_list = list of teammates

r = Implementation()

# %%
import os
if isolated !=1:
    file_path = os.path.join(os.getcwd(), "rating_list.txt")
    tmp_dict = {}

    with open(file_path, "r") as file:
        for line in file:
            name, rating = line.strip().split(": ")
            tmp_dict[name] = float(rating)


# %%
for name, ppl in teams.items():
    for person in ppl:
        if person not in tmp_dict:
            r.addPlayer(person, 1500)
        else:
            r.addPlayer(person, tmp_dict[person])
print(r.getRatingList())

# %%
import matplotlib.pyplot as plt

for name, matches in school_history.items():
    rounds = len(matches)
    break
for i in range(rounds):
    try:
        for name, matches in school_history.items():
            opp = matches[i]
            opp = remove_prefix(opp, "Won against ")
            opp = remove_prefix(opp, "Lost against ")
            if matches[i].startswith("Won"):
                for person in teams[name]:
                    for opp_person in teams[opp]:
                        r.recordMatch(person, opp_person, winner=person)
            else:
                for person in teams[name]:
                    for opp_person in teams[opp]:
                        r.recordMatch(person, opp_person, winner=opp_person)
    except:
        pass
    r.applyUpdates()
    print(f"round {i+1} done")
    print(r.getRatingList())

    ratings = r.getRatingList()
    rating_values = [rating[1] for rating in ratings]

    # plt.hist(rating_values, bins=10)
    # plt.xlabel("Rating")
    # plt.ylabel("Frequency")
    # plt.title("Distribution of Ratings for round " + str(i + 1))
    # plt.show()


# %%
rank_list = sorted(r.getRatingList(), key=lambda x: x[1], reverse=True)
for rank in rank_list:
    print(rank[0], rank[1])

# %%
import os
if isolated !=1:
    file_path = os.path.join(os.getcwd(), "rating_list.txt")

    rating_dict = {}

    with open(file_path, "r") as file:
        for line in file:
            name, rating = line.strip().split(": ")
            rating_dict[name] = float(rating)

    for name, rating in r.getRatingList():
        rating_dict[name] = float(rating)

    with open(file_path, "w") as file:
        for name, rating in rating_dict.items():
            file.write(f"{name}: {rating}\n")
else:
    tournament_path = os.path.join(os.getcwd(), f"{website_url}.txt")
    for name, rating in r.getRatingList():
        print(f"{name}: {rating}")
    with open(tournament_path, "w") as file:
        file.write(f"{name}: {rating}\n")
    print(f"saved to {tournament_path}")