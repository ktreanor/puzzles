from itertools import permutations
from spellchecker import SpellChecker

def jumble_solver(scrambled):
    """Jumble Solver is a word unscrambler tool that can be used for word games or solving anagrams.

    :param scrambled: The jumbled word that needs to be unscrambled
    :type guess: str
    :return: The unscrambled word
    :rtype: str
    """

    # Use the permutations function to come up with all possible combinations of letter from the jumble
    # Then use the map function on the combinations to turn them into an iterable of strings (not a list, but a map)
    all_permutations = map(''.join, permutations(scrambled))

    # Use the spell check function to grab only real words
    spell = SpellChecker()
    answer = spell.known(all_permutations)

    # Assuming there is only one solution in a Jumble puzzle so just return the first (and only) word
    return answer.pop()

if __name__ == "__main__":
    # Test the jumble_solver function

    letter_list = ''

    for i in range(4):
        jumble = input(f"Enter a jumbled word #{i+1}: ")
        print(f'[+] {jumble_solver(jumble)}')
        letters = input("Enter the circled letters: ")
        letter_list += letters

    print(f'Final Answer: {jumble_solver(letter_list)}')
