import string

ALPHABET_LOWER = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_UPPER = ALPHABET_LOWER.upper()
ALPHABET_LOWER_ARR = list(ALPHABET_LOWER)
ALPHABET_UPPER_ARR = list(ALPHABET_UPPER)


class Caesar:

    def __init__(self):
        self.id = 1

    async def create(self, text, upper=True):
        self.upper = upper
        if (self.upper):
            self.text = text.upper()
            self.workingArray = ALPHABET_UPPER_ARR
        else:
            self.text = text.lower()
            self.workingArray = ALPHABET_LOWER_ARR

    def convertToType(self, text):
        if self.upper:
            return text.upper()
        else:
            return text.lower()

    async def encode(self, shift):
        if shift > len(self.workingArray):
            return
        newStr = []
        for char in self.text:
            if char in string.punctuation or char == " " or char == ' ':
                newStr.append(char)
                continue
            if self.workingArray.index(char) + shift >= len(self.workingArray):
                over = (self.workingArray.index(char) + shift) - len(self.workingArray)
                newChar = self.workingArray[over]
            else:
                newChar = self.workingArray[self.workingArray.index(char) + shift]
            newStr.append(newChar)

        self.encoded = "".join(newStr)

    async def decode(self, shift):
        if shift > len(self.workingArray):
            return

        newStr = []
        for char in self.text:
            if char == " ":
                newStr.append(char)
                continue
            index = self.workingArray.index(char)
            if index - shift < 0:
                over = (index - shift) + 26
                newChar = self.workingArray[over]
            else:
                newChar = self.workingArray[self.workingArray.index(char) - shift]
            newStr.append(newChar)

        self.decoded = "".join(newStr)

    async def bruteForce(self):
        wordsDir = "bot/resources/common_words.txt"
        word = self.text.translate(string.punctuation)
        wordArr = word.split(" ")
        bestScore = 0
        shift = 0
        for i in range(0, len(self.workingArray)):
            score = 0
            for word in wordArr:
                newWord = self.decodeWord(word, i)
                with open(wordsDir) as f:
                    for line in f:
                        line = line.rstrip("\n ")
                        if newWord == self.convertToType(line):
                            score += 1
            if score > bestScore:
                bestScore = score
                shift = i

        self.shift = shift
        await self.decode(shift)

    def decodeWord(self, word, shift):
        newStr = []
        for char in word:
            index = self.workingArray.index(char)
            if index - shift < 0:
                over = (index - shift) + 26
                newChar = self.workingArray[over]
            else:
                newChar = self.workingArray[self.workingArray.index(char) - shift]
            newStr.append(newChar)

        return "".join(newStr)
