import requests

def test_python(type):
    url = f'http://localhost:8000/{type}'
    data = {
        "type": "python",
        "solution": "print(input())",
        "input": "a",
        "expected_output": "a"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()['success']
    assert response.json()['run_success']

    data = {
        "type": "python",
        "solution": "print(input())",
        "input": "a",
        "expected_output": "b"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert not response.json()['success']
    assert response.json()['run_success']
  

def test_real_code():
    from auto_evaluators.code.utils import load_test_case_io_pairs_from_zip
    test_case_zip_path = "/sgl-workspace/data/test_cases/darkbzoj/2378.zip"
    all_io_pairs = load_test_case_io_pairs_from_zip(test_case_zip_path)

    code = open("examples/code_judge/solution2378.py", "r").read()

    for input_str, expected_output in all_io_pairs:
        url = 'http://localhost:8000/judge'
        data = {
            "type": "python",
            "solution": code,
            "input": input_str,
            "expected_output": expected_output
        }
        response = requests.post(url, json=data)
        print(response.json())
        assert response.status_code == 200
        # assert response.json()['success']
        # assert response.json()['run_success']


def test_batch(type):
    url = f'http://localhost:8000/{type}/batch'
    data = {
        'type': 'batch',
        "submissions": [{
        "type": "cpp",
        "solution": """#include <cstdio>
int main(){printf("a");return 0;}
""",
        "expected_output": "b"
        }, {
        "type": "python",
        "solution": "print(input())",
        "input": "a",
        "expected_output": "b"
        }, {
            "type": "python",
            "solution": "print(input())",
            "input": "a",
            "expected_output": "a"
        }, {
            "type": "cpp",
            "solution": """#include <cstdio>
#include <unistd.h>
int main(){sleep(3);printf("a");return 0;}
""",
            "expected_output": "a"
        }]
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    results = response.json()['results']

    assert len(results) == 4
    assert not results[0]['success']
    assert results[0]['run_success']
    assert not results[1]['success']
    assert results[1]['run_success']
    assert results[2]['success']
    assert results[2]['run_success']
    assert results[3]['success']
    assert results[3]['run_success']


def test_real_code_batched():
    from auto_evaluators.code.utils import load_test_case_io_pairs_from_zip
    test_case_zip_path = "/sgl-workspace/data/test_cases/darkbzoj/2378.zip"
    all_io_pairs = load_test_case_io_pairs_from_zip(test_case_zip_path)

    # code = open("examples/code_judge/solution2378.py", "r").read()
    code = open("examples/code_judge/solution2378.cpp", "r").read()

    # Prepare batch submissions using the same test cases as test_real_code
    submissions = []
    for input_str, expected_output in all_io_pairs:
        submission = {
            "type": "cpp",
            "solution": code,
            "input": input_str,
            "expected_output": expected_output
        }
        submissions.append(submission)

    # Send batch request
    url = 'http://localhost:8000/judge/long-batch'
    data = {
        'type': 'batch',
        "submissions": submissions
    }
    
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    
    results = response.json()['results']
    assert len(results) == len(all_io_pairs)
    
    # Print results for each test case
    for i, result in enumerate(results):
        # print(f"Test case {i+1}: success={result['success']}, run_success={result['run_success']}")
        print(f"Test case {i}: {result}")
        # Uncomment these assertions if you want to ensure all test cases pass
        # assert result['success']
        # assert result['run_success']


if __name__ == "__main__":
    # test_python("judge")
    # test_real_code()
    test_real_code_batched()