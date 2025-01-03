import os
import wordfreq
import operator

from itertools import chain
from collections import Counter

# Colors for the terminal output
GREEN = '\033[32m'
YELLOW = '\033[33m'
GREY = '\033[37m'
RESET = '\033[0m'

class WordleSolver:
    """Wordle Solver is a tool that can be used to help solve the Wordle game. Wordle is a word puzzle game where the player has 6 chances to guess a 5 letter word. After each guess, the player is given feedback on the guess. A green letter means the letter is in the correct spot, a yellow letter means the letter is in the word but in the wrong spot, and a gray letter means the letter is not in the word at all. The player can use this feedback to make a better guess on the next turn
    """

    # Valid words are all the words that the game accepts as guesses
    __valid_words = []
    __working_list = []

    # Dictionaries used for recommendation strategies
    __letter_count = {}
    __scored_words = {}

    # Current guess, and how many guesses have been made used during gameplay
    __current_guess = ''
    __guess_number = 0

    def __init__(self):
        """Initializes the WordleSolver class, loads the valid words, and prepares the game"""

        # Get the path for the valid words csv
        # This is a list of all the words that the game will accept as guesses
        valid_words_file = os.path.join(os.path.dirname(__file__), "valid_words.csv")

        # Open the valid words file and load into the list
        with open(valid_words_file) as valid_words:
            self.__valid_words.extend(valid_words.read().splitlines())

        # Prepare all the lists and dictionaries to play
        self.__prepare_game()

    def __prepare_game(self):
        """Gets everything set up for playing the game, loads the dictionaries and clears the working list"""

        # Clear the working list
        self.__working_list.clear()

        # Start the working list with all the words in the valid words list
        self.__working_list.extend(self.__valid_words)

        # Create the initial work scoring used in the recommendations
        self.__score_words()

    def __get_letter_usage(self):
        """Creates a dictionary of letters with how often it's used in the working list"""

        # The from_iterable function will turn all the words into a single list of letters, then the counter creates a dictionary with the count of each letter
        return Counter(chain.from_iterable(self.__working_list))

    def __get_word_score(self, word: str) -> int:
        """Scores a word based on the frequency of the letters in the word and how common the word is in the English language.

        Args:
            word (str): The word to score.

        Returns:
            int: The score of the word.
        """

        score = 0

        # Remove all duplicate letters in the word then turn it into a list (Removing duplicates avoids making recommendations with multiple e's for example)
        for letter in list(set(word)):
            score += self.__letter_count[letter]

        # Give common words a slightly higher score to increase their likelihood of being recommended
        # Magic number here, but after running a lot of simulations multiplying the word frequency by 2 gave the highest win rate
        score += wordfreq.zipf_frequency(word, "en") * 2
        return score

    def __score_words(self):
        """Loops through all the words in the working list and scores them based on letter frequency and how common the word is in the english language"""

        # Clear the old values
        self.__letter_count.clear()
        self.__scored_words.clear()

        self.__letter_count = self.__get_letter_usage()

        # Loops through the working list and creates a dictionary with the word's score
        for word in self.__working_list:
            self.__scored_words[word] = self.__get_word_score(word)

        # self.__scored_words = [self.__get_word_score(word) for word in self.__working_list]

    def __gray_letter(self, letter: str):
        """Filters the working list when a letter in a guess is marked as grey, meaning it doesn't exist in the puzzle word.

        Args:
            letter (str): Letter that doesn't exist in the puzzle word.
        """
        temp_list = []

        # Loop through all the words in the working list and find only those that do NOT have the letter
        for word in self.__working_list:
            if letter not in word:
                temp_list.append(word)

        # update the working list
        self.__working_list.clear()
        self.__working_list.extend(temp_list)

    def __green_letter(self, letter, location):
        """
        Filters the working list when a letter in a guess is marked as green, meaning it is in the right spot of the puzzle word.

        Args:
            letter (str): Letter in the correct location of the puzzle word.
            location (int): Location of the letter in the puzzle.
        """
        temp_list = []

        # Loop through all the words in the working list and find only those that have the letter in the given spot
        for word in self.__working_list:
            if word[location] == letter:
                temp_list.append(word)

        # update the working list
        self.__working_list.clear()
        self.__working_list.extend(temp_list)

    def __yellow_letter(self, letter, location):
        """Filters the working list when a letter in a guess is marked as yellow, meaning it is in the puzzle word, but not in the spot guessed.

        Args:
            letter (str): Letter in the correct location of the puzzle word.
            location (int): Location that the letter was used.
        """
        temp_list = []

        # Loop through all the words in the working list and find words that do NOT have the letter in that spot.
        for word in self.__working_list:
            if word[location] != letter:
                # Make sure the letter appears somewhere else in the word
                if letter in word:
                    temp_list.append(word)

        # update the working list and clear the temp list
        self.__working_list.clear()
        self.__working_list.extend(temp_list)

    def __refine_working_list(self, guess: str, result_key: str):
        """Filters the working list based on a guessed word, and the result key returned from the puzzle.

        Args:
            guess (str): The word guessed by the user.
            result_key (str): The key returned by the puzzle consisting of '-' if the letter doesn't appear in the word, 'g' if it is in the right spot, and 'y' if it exists in the puzzle word but is in the wrong location.
        """
        # Loop through all 5 letters result_key and perform the proper function
        for index in range(0, 5):
            if (result_key[index]) == "-":
                self.__gray_letter(guess[index])
            elif (result_key[index]) == "y":
                self.__yellow_letter(guess[index], index)
            else:
                self.__green_letter(guess[index], index)

        # Re-score the words to take into account the change in letter distribution
        self.__score_words()

    def __get_recommendation(self, rec_count: int) -> dict:
        """Returns the top recommendations for the next guess.

        Args:
            rec_count (int): How many recommendations the user would like to see.

        Returns:
            dict: A dictionary of the top recommended words and their scores.
        """
        return dict(
            sorted(self.__scored_words.items(), key=lambda item: item[1], reverse=True)[
                :rec_count
            ]
        )

    @property
    def recommendation(self) -> str:
        """The best recommendation for the next guess."""

        return max(self.__scored_words.items(), key=operator.itemgetter(1))[0]

    def enter_guess(self, word: str):
        """Enters a guess into the wordle solver.

        Args:
            word (str): The word to guess.
        """

        self.__current_guess = word
        self.__guess_number += 1

    def enter_result(self, result_key: str):
        """Enters the result of a wordle guess and refines the working list.

        Args:
            result_key (str): String representing the results from a wordle guess, for example: '--g-y'.
        """

        self.__refine_working_list(self.__current_guess, result_key)

    @property
    def guess_number(self) -> int:
        """The number of guesses made so far in the wordle game."""
        return self.__guess_number

    @property
    def remaining_possible_words(self) -> int:
        """The number of possible solutions remaining to the wordle puzzle."""

        return len(self.__working_list)

if __name__ == "__main__":
    wordle = WordleSolver()
    result_key = ''

    show_instructions = input('Welcome to the Wordle Solver, would you like to learn how to cheat? (Y/N): ')

    if show_instructions == 'Y' or show_instructions == 'y':
        print('')
        print('Wordle Sover will start each round by telling you how many words could be correct')
        print('and give you a recomendation, it will then ask you which word you played (just hit enter if you played the recomendation)')
        print('')
        print('It will then ask you what the results of your guess was, you should enter the following')
        print(GREEN + "   If \u2588 (correct letter, correct spot)" + RESET + " enter 'g'")
        print(YELLOW + "   if \u2588 (correct letter, wrong spot)" + RESET + " enter 'y'")
        print(GREY + "   if \u2588 (letter not in the word)" + RESET + " enter '-'")
        print('')

    print(f'There are {wordle.remaining_possible_words:,} possible solutions, we recomend: {wordle.recommendation}')

    while wordle.guess_number < 6 and result_key != 'ggggg':
        guess = input(f"What did you enter for guess #{wordle.guess_number + 1}: ") or wordle.recommendation
        wordle.enter_guess(guess)
        result_key = input('What was the result: ')
        wordle.enter_result(result_key)
        print('')
        print(f'There are {wordle.remaining_possible_words:,} possible solutions, we recommend {wordle.recommendation}')
