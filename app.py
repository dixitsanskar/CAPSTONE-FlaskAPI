from flask import Flask, request, jsonify
import re
import csv
from flask import g

app = Flask(__name__)

def extract_keywords(text):
    stopwords = {'and', 'the', 'is', 'of', 'or', 'in', 'to', 'it', 'that', 'was', 'with', 'for', 'on', 'as', 'by', 'at', 'an', 'but', 'not', 'are', 'you', 'we', 'can', 'have', 'has', 'this'}
    keywords = re.findall(r'\b\w+\b', text.lower())
    keywords = [keyword for keyword in keywords if keyword not in stopwords]
    return keywords

def load_problem_statements_from_csv(csv_file):
    unique_problem_statements = set()
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            author = row.get('Author', '')
            title = row.get('Title', '')
            problem_statement = row.get('Problem Statement', '')
            contributor = row.get('Contributor', '')
            
            statement = f"{author} - {title} - {problem_statement} - {contributor}"
            unique_problem_statements.add(statement)
    return list(unique_problem_statements)

def calculate_percentage_match(input_keywords, statement_keywords):
    if len(input_keywords) == 0:
        return 0.0
    match_percentage = (len(set(input_keywords) & set(statement_keywords)) / len(input_keywords)) * 100
    return round(match_percentage, 2)

def search_problem_statements(input_text, problem_statements, min_percentage=20, page=1, results_per_page=10):
    input_keywords = extract_keywords(input_text)

    matching_statements = []
    # start_index = (page - 1) * results_per_page
    # end_index = start_index + results_per_page


    for statement in problem_statements:
        statement_keywords = extract_keywords(statement)

        if any(keyword in statement_keywords for keyword in input_keywords):
            match_percentage = calculate_percentage_match(input_keywords, statement_keywords)
            if match_percentage > min_percentage:
                data = statement.split(' - ')
                matching_statements.append({
                    'percentage': match_percentage,
                    'title': data[1],
                    'author': data[0],
                    'problem_statement': data[2],
                    'contributor': data[3] if len(data) > 3 else ''
                })

    matching_statements.sort(key=lambda x: x['title'])
    return matching_statements

def get_problem_statements():
    statements = getattr(g, '_problem_statements', None)
    if statements is None:
        statements = load_problem_statements_from_csv('./ps.csv')
        g._problem_statements = statements
    return statements

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    input_text = data.get('input_text', '')
    min_percentage = data.get('min_percentage', 20)
    page = data.get('page', 1)

    problem_statements = get_problem_statements()

    results = search_problem_statements(input_text, problem_statements, min_percentage, page)

    if results:
        for i, statement in enumerate(results, start=1):
            print(f"{i}. Title: {statement['title']}, Author: {statement['author']}, Problem Statement: {statement['problem_statement']}, Contributor: {statement['contributor']}")

        response = {'status': 'success', 'results': results}
    else:
        response = {'status': 'error', 'message': 'No matching problem statements found.'}

    return jsonify(response)

# if __name__ == '__main__':
#     app.run(debug=True)
