scores = {"Chinese": 85, "Math": 90, "English": 78}

# 01. Accessing values in a dictionary
for subject in scores.keys():
    print(subject)  # Output: Chinese, Math, English
# 02. Accessing values in a dictionary
for score in scores.values():
    print(score)  # Output: 85, 90, 78
# 03. Accessing key-value pairs in a dictionary
for subject, score in scores.items():
    print(f"{subject}: {score}")  # Output: Chinese: 85, Math: 90, English: 78