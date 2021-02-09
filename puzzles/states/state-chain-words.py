#!/usr/bin/env python3
#
# Generates a list of words comprised of letters that are formed from chains of
# the two-letter postal abbreviations of US states.  Each chain starts with a
# state, followed by an adjacent state, followed by a state adjacent to the
# second state, etc.  The default chain length is four, but you can pass an
# integer argument to override it to a shorter or longer value.  Values greater
# than 7 start to perform badly as the graph of adjacent states explodes to
# huge numbers.
#

import sys
import re

class State:
    def __init__(self, name, abbr, neighbors):
        self.name = name
        self.abbr = abbr
        self.neighbors = list() if neighbors is None else neighbors

    def get_name(self):
        return self.name

    def get_abbr(self):
        return self.abbr

    def get_neighbors(self):
        return self.neighbors

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"{self.name} ({self.abbr}) {', '.join(sorted(list(self.neighbors)))}"

#
# Taken from here:
#   https://thefactfile.org/u-s-states-and-their-border-states/
#
#   (excluding water border states)
#
states_and_neighbors = {
    "Alabama":        State("Alabama",        "AL", ["Mississippi", "Tennessee", "Florida", "Georgia"]),
    "Alaska":         State("Alaska",         "AK", None),
    "Arizona":        State("Arizona",        "AZ", ["Nevada", "New Mexico", "Utah", "California", "Colorado"]),
    "Arkansas":       State("Arkansas",       "AR", ["Oklahoma", "Tennessee", "Texas", "Louisiana", "Mississippi", "Missouri"]),
    "California":     State("California",     "CA", ["Oregon", "Arizona", "Nevada"]),
    "Colorado":       State("Colorado",       "CO", ["New Mexico", "Oklahoma", "Utah", "Wyoming", "Arizona", "Kansas", "Nebraska"]),
    "Connecticut":    State("Connecticut",    "CT", ["New York", "Rhode Island", "Massachusetts"]),
    "Delaware":       State("Delaware",       "DE", ["New Jersey", "Pennsylvania", "Maryland"]),
    "Florida":        State("Florida",        "FL", ["Georgia", "Alabama"]),
    "Georgia":        State("Georgia",        "GA", ["North Carolina", "South Carolina", "Tennessee", "Alabama", "Florida"]),
    "Hawaii":         State("Hawaii",         "HI", None),
    "Idaho":          State("Idaho",          "ID", ["Utah", "Washington", "Wyoming", "Montana", "Nevada", "Oregon"]),
    "Illinois":       State("Illinois",       "IL", ["Kentucky", "Missouri", "Wisconsin", "Indiana", "Iowa", "Michigan"]),
    "Indiana":        State("Indiana",        "IN", ["Michigan", "Ohio", "Illinois", "Kentucky"]),
    "Iowa":           State("Iowa",           "IA", ["Nebraska", "South Dakota", "Wisconsin", "Illinois", "Minnesota", "Missouri"]),
    "Kansas":         State("Kansas",         "KS", ["Nebraska", "Oklahoma", "Colorado", "Missouri"]),
    "Kentucky":       State("Kentucky",       "KY", ["Tennessee", "Virginia", "West Virginia", "Illinois", "Indiana", "Missouri", "Ohio"]),
    "Louisiana":      State("Louisiana",      "LA", ["Texas", "Arkansas", "Mississippi"]),
    "Maine":          State("Maine",          "ME", ["New Hampshire"]),
    "Maryland":       State("Maryland",       "MD", ["Virginia", "West Virginia", "Delaware", "Pennsylvania"]),
    "Massachusetts":  State("Massachusetts",  "MA", ["New York", "Rhode Island", "Vermont", "Connecticut", "New Hampshire"]),
    "Michigan":       State("Michigan",       "MI", ["Ohio", "Wisconsin", "Illinois", "Indiana"]),
    "Minnesota":      State("Minnesota",      "MN", ["North Dakota", "South Dakota", "Wisconsin", "Iowa"]),
    "Mississippi":    State("Mississippi",    "MS", ["Louisiana", "Tennessee", "Alabama", "Arkansas"]),
    "Missouri":       State("Missouri",       "MO", ["Nebraska", "Oklahoma", "Tennessee", "Arkansas", "Illinois", "Iowa", "Kansas", "Kentucky"]),
    "Montana":        State("Montana",        "MT", ["South Dakota", "Wyoming", "Idaho", "North Dakota"]),
    "Nebraska":       State("Nebraska",       "NE", ["Missouri", "South Dakota", "Wyoming", "Colorado", "Iowa", "Kansas"]),
    "Nevada":         State("Nevada",         "NV", ["Idaho", "Oregon", "Utah", "Arizona", "California"]),
    "New Hampshire":  State("New Hampshire",  "NH", ["Vermont", "Maine", "Massachusetts"]),
    "New Jersey":     State("New Jersey",     "NJ", ["Pennsylvania", "Delaware", "New York"]),
    "New Mexico":     State("New Mexico",     "NM", ["Oklahoma", "Texas", "Utah", "Arizona", "Colorado"]),
    "New York":       State("New York",       "NY", ["Pennsylvania", "Vermont", "Connecticut", "Massachusetts", "New Jersey"]),
    "North Carolina": State("North Carolina", "NC", ["Tennessee", "Virginia", "Georgia", "South Carolina"]),
    "North Dakota":   State("North Dakota",   "ND", ["South Dakota", "Minnesota", "Montana"]),
    "Ohio":           State("Ohio",           "OH", ["Michigan", "Pennsylvania", "West Virginia", "Indiana", "Kentucky"]),
    "Oklahoma":       State("Oklahoma",       "OK", ["Missouri", "New Mexico", "Texas", "Arkansas", "Colorado", "Kansas"]),
    "Oregon":         State("Oregon",         "OR", ["Nevada", "Washington", "California", "Idaho"]),
    "Pennsylvania":   State("Pennsylvania",   "PA", ["New York", "Ohio", "West Virginia", "Delaware", "Maryland", "New Jersey"]),
    "Rhode Island":   State("Rhode Island",   "RI", ["Massachusetts", "Connecticut"]),
    "South Carolina": State("South Carolina", "SC", ["North Carolina", "Georgia"]),
    "South Dakota":   State("South Dakota",   "SD", ["Nebraska", "North Dakota", "Wyoming", "Iowa", "Minnesota", "Montana"]),
    "Tennessee":      State("Tennessee",      "TN", ["Mississippi", "Missouri", "North Carolina", "Virginia", "Alabama", "Arkansas", "Georgia", "Kentucky"]),
    "Texas":          State("Texas",          "TX", ["New Mexico", "Oklahoma", "Arkansas", "Louisiana"]),
    "Utah":           State("Utah",           "UT", ["Nevada", "New Mexico", "Wyoming", "Arizona", "Colorado", "Idaho"]),
    "Vermont":        State("Vermont",        "VT", ["New Hampshire", "New York", "Massachusetts"]),
    "Virginia":       State("Virginia",       "VA", ["North Carolina", "Tennessee", "West Virginia", "Kentucky", "Maryland"]),
    "Washington":     State("Washington",     "WA", ["Oregon", "Idaho"]),
    "West Virginia":  State("West Virginia",  "WV", ["Pennsylvania", "Virginia", "Kentucky", "Maryland", "Ohio"]),
    "Wisconsin":      State("Wisconsin",      "WI", ["Michigan", "Minnesota", "Illinois", "Iowa"]),
    "Wyoming":        State("Wyoming",        "WY", ["Nebraska", "South Dakota", "Utah", "Colorado", "Idaho", "Montana"])
}

def build_neighbor_chains(chain_length):
    chains = []

    # Iterate over all of the US states.
    #
    for state in states_and_neighbors.values():
        new_chain = []       # Start with a new (empty) chain at the top level.
        states_seen = set()  # Set of states that we have already seen in this chain.
        traverse_neighbor_chain(state, states_seen, chains, new_chain, chain_length-1)

    return chains

#
# Recursively traverse the chain of neighbors of a given state.
#
def traverse_neighbor_chain(state, states_seen, chains, chain, max_depth):
    # Add ourself to the end of the current chain.
    chain.append(state)

    # If we are at the end of the current chain of neighbors, add our chain
    # to the list of chains and return.
    #
    if max_depth == 0:
        chains.append(chain)
        return

    # For this chain, add the current state to the set of states that have
    # already been seen, so that we don't repeat it.
    #
    states_seen.add(state)

    for neighbor_name in state.get_neighbors():
        neighbor = states_and_neighbors[neighbor_name]

        # Avoid visiting the same state more than once in the same chain of
        # states.
        #
        if neighbor in states_seen:
           continue

        # At every branch we need to create a local copy of the set of states
        # seen.  This avoids the situation where we skip a state in one chain
        # because it has already been seen already in a different chain
        # starting with the same state.  This caused a very confusing bug, made
        # even weirder by the fact that I was storing neighboring states in a
        # set, which uses hashing.  The hash function appears to be seeded with
        # a random number each time the program is executed, causing the order
        # of neighbors to be differen each time, and thus the states that had
        # already been seen to also be different.  The result was that each
        # time it ran, it could produce a slightly different set of words.  I
        # changed the neighboring states to be stored in a list to remove the
        # nondeterminism.
        #
        local_states_seen = states_seen.copy()
        local_chain = chain.copy()
        traverse_neighbor_chain(neighbor, local_states_seen, chains, local_chain, max_depth-1)

#
# Main routine
#
if __name__ == "__main__":
    chain_length = 4
    word_file_name = "/usr/share/dict/words"

    if len(sys.argv) > 1:
        chain_length = int(sys.argv[1])

    if len(sys.argv) > 2:
        word_file_name = sys.argv[2]

    chains = build_neighbor_chains(chain_length)

    # Dictionary of anagrams.
    #
    anagrams = dict()

    # Source of valid words.
    #
    word_file = open(word_file_name, "r")

    # A word's key is generated by sorting its letters and concatenating them,
    # so a word and all of its anagrams will have the same key.
    #
    def generate_key(string):
        letters = [char for char in string]
        letters.sort()
        key = "".join(letters).upper()
        return key


    # Valid words must only contain upper-case letters and have a length
    # that is twice the chain length (because US state abbreviations are
    # all two characters long).  This could probably be implemented more
    # efficiently without regular expressions, but for the relatively small
    # number of words in most dictionary files it performs well enough.
    #
    word_length = chain_length * 2
    regex = "^[A-Z]{%d}$" % word_length

    pattern = re.compile(regex)

    # Read all words in the dictionary file, filtering for only valid words.
    #
    for line in word_file:
        word = line.strip().upper()

        # Skip words that have the wrong length.
        #
        if len(word) != word_length:
            continue

        if pattern.match(word):
            key = generate_key(word)

            if key in anagrams:
                anagrams[key].append(word)
            else:
                anagrams[key] = [ word ]


    total_found_words = set()

    for chain in chains:
        chain_abbrs = list(map(lambda s: s.get_abbr(), chain))
        chain_string = "".join(chain_abbrs)

        found_words = set()

        key = generate_key(chain_string)
        if key in anagrams:
            words = anagrams[key]
            print(", ".join(chain_abbrs), ":", ", ".join(words))

            for word in words:
                found_words.add(word)
                total_found_words.add(word)

    if len(total_found_words) > 0:
        print()
        print("All words:")
        for word in total_found_words:
            print(f"    {word}")
    else:
        print("No words found.")

