# Python Code:
# You've discovered a series of ancient symbols etched into the wall. They seem to follow a pattern, and you believe deciphering this pattern is key to unlocking the next chamber.
# The symbols are represented as a list of numbers. Your task is to write a function that identifies the pattern and predicts the next number in the sequence.
# HINTS: Look for arithmetic or geometric progressions. Consider differences between consecutive numbers.

def predict_next_symbol(symbols):
    # Calculate the differences between consecutive symbols
    differences = [symbols[i+1] - symbols[i] for i in range(len(symbols)-1)]
    
    # Check if the differences are constant (arithmetic progression)
    if len(set(differences)) == 1:
        next_symbol = symbols[-1] + differences[0]
        return next_symbol
    
    # If not an arithmetic progression, check for a geometric progression
    # Avoid division by zero
    ratios = [symbols[i+1] / symbols[i] for i in range(len(symbols)-1) if symbols[i] != 0]
    if ratios and len(set(ratios)) == 1:
        next_symbol = symbols[-1] * ratios[0]
        return int(next_symbol)  # Return as integer
    
    # If neither, return None
    return None

# Example usage:
symbols = [2, 4, 6, 8]
next_symbol = predict_next_symbol(symbols)
print(f"The next symbol is: {next_symbol}")

### START OF USER CODE ###

next_symbol = predict_next_symbol(symbols)
if next_symbol is not None:
    print(f"The next symbol in the sequence is: {next_symbol}")
else:
    print("Could not determine the next symbol.")

### END OF USER CODE ###