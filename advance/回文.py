def palindrome(s: str) -> bool:
    cleaned = "".join(char.lower() for char in s if char.isalnum())

    left, right = 0, len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True
print(palindrome("A man, a plan, a canal: Panama"))
print(palindrome("race a car"))