#!/usr/bin/env python3 -W ignore::DeprecationWarning
import sys
from open_questions import QuestionGenerator
import random

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: ./ask ARTICLE.txt NUM_QUESTIONS")
        sys.exit(1)

    article_txt = sys.argv[1]
    num_questions = int(sys.argv[2])

    with open(article_txt, 'r', encoding='utf8') as f:
        article_txt = f.read()

    questions_generated = QuestionGenerator(article_txt).get_questions()
    for i in range(len(questions_generated)):
        print(questions_generated[i][1], questions_generated[i][0])
        pass

    # TODO: rank the questions before printing

    if len(questions_generated) < num_questions:
        for i in range(num_questions - len(questions_generated)):
            print(3, random.choice(questions_generated))

# TODO: rename file to ask