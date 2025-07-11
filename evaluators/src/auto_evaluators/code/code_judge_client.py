import requests
import dataclasses
import enum
import collections
from time import time
from pathlib import Path
from typing import List, Dict
import uuid


from auto_evaluators.code.utils import load_test_case_io_pairs_from_zip
from auto_evaluators.code.code_judge_client_async import QueuedJudgeClient, Submission, SubmissionResult


def test_cpp(url):
    # url = f'http://localhost:8000/{type}'
    data = {
        "type": "cpp",
        "solution": """#include <cstdio>
#include <unistd.h>
int main(){sleep(3);printf("a");return 0;}
""",
        "expected_output": "a"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()['run_success']
    assert response.json()['success']

    data = {
        "type": "cpp",
        "solution": """#include <cstdio>
int main(){printf("a");return 0;}
""",
        "expected_output": "b"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()['run_success']
    assert not response.json()['success']

    # compile error
    data = {
        "type": "cpp",
        "solution": """#include <cstdio>
int main(){printf("a")xx;return 0;}
""",
        "expected_output": "b"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert not response.json()['run_success']
    assert not response.json()['success']


def test_python(url):
    # url = f'http://localhost:8000/{type}'
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


def test_python_timeout(url):
    # url = f'http://localhost:8000/{type}'
    data = {
        "type": "python",
        "solution": "print(input())",
        "input": "",
        "expected_output": "a"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert not response.json()['success']
    assert not response.json()['run_success']


def test_batch(url):
    # url = f'http://localhost:8000/{type}/batch'
    url = url + '/long-batch'
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


def test_batch_timeout(url):
    # url = f'http://localhost:8000/{type}/batch'
    url = url + '/long-batch'
    data = {
        'type': 'batch',
        "submissions": [{
        "type": "python",
        "solution": "print(input())",
        "input": "",
        "expected_output": "b"
        }, {
            "type": "python",
            "solution": "print(input())",
            "input": "a",
            "expected_output": "a"
        }, {
        "type": "python",
        "solution": "print(input())",
        "input": "",
        "expected_output": "b"
        }, {
            "type": "python",
            "solution": "print(input())",
            "input": "a",
            "expected_output": "a"
        },{
        "type": "python",
        "solution": "print(input())",
        "input": "",
        "expected_output": "b"
        }, {
            "type": "python",
            "solution": "print(input())",
            "input": "a",
            "expected_output": "a"
        }]
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200, f"Response: {response}"
    results = response.json()['results']

    assert len(results) == 6
    assert not results[0]['success']
    assert not results[0]['run_success']
    assert results[1]['success']
    assert results[1]['run_success']
    assert not results[2]['success']
    assert not results[2]['run_success']
    assert results[3]['success']
    assert results[3]['run_success']
    assert not results[4]['success']
    assert not results[4]['run_success']
    assert results[5]['success']
    assert results[5]['run_success']


def test_multi_process(url):
    # url = f'http://localhost:8000/{type}'
    code = """
from time import sleep
import os
from multiprocessing import Process


def worker():
    print('Worker process started')
    sleep(100)
    print('Worker process finished')


print('PP: Starting worker process')
# Start a worker process
p = Process(target=worker)
p.start()
print('worker:', os.getpid())
sleep(1)
print('PP: Worker process Finished, but leaving its child process running')
"""
    data = {
        "type": "python",
        "solution": code,
        "input": "",
        "expected_output": "a"
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert not response.json()['success']
    assert not response.json()['run_success']


def test_io_valid(url):
    # url = f'http://localhost:8000/{type}'
    code = """
with open('test.txt', 'w') as f:
    f.write('Hello, world!')
"""
    data = {
        "type": "python",
        "solution": code,
        "input": "",
        "expected_output": ""
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200
    assert response.json()['success']
    assert response.json()['run_success']


def test_io_invalid(url):
    test_file = Path('/tmp/test.txt')
    test_file.unlink(missing_ok=True)
    # url = f'http://localhost:8000/{type}'
    code = """
import pathlib
print(pathlib.Path('.').resolve())
with open('../test.txt', 'w') as f:
    f.write('Hello, world!')
"""
    data = {
        "type": "python",
        "solution": code,
        "input": "",
        "expected_output": ""
    }
    response = requests.post(url, json=data)
    print(response.json())
    assert response.status_code == 200

    print(f"Jailbreak Status: {Path('/tmp/test.txt').exists()}")


def test_all(original_url):
  for typ in ['run', 'judge']:
    url = f"{original_url}/{typ}"
    start = time()
    test_batch_timeout(url)
    end = time()
    print(f'Time taken: {end - start} seconds')
    test_cpp(url)
    test_python(url)
    test_batch(url)
    test_python_timeout(url)
    test_multi_process(url)
    test_io_valid(url)
    test_io_invalid(url)


# create a enum class as JudgeResultType
class JudgeResultType(enum.Enum):
    AC = 0
    WA = 1
    ER = 2
    TLE = 3
    # online judge error
    OJE = 4


JudgeResultTypeToHumanReadable = {
    JudgeResultType.AC: "Accepted",
    JudgeResultType.WA: "Wrong Answer",
    JudgeResultType.ER: "Compile/Runtime Error",
    JudgeResultType.TLE: "Time Limit Exceeded",
    JudgeResultType.OJE: "Judge System Error"
}


@dataclasses.dataclass
class DarkbzojSubmission:
  code: str
  problem_id: str
  lang: str = 'python'  # default to python, can be 'cpp'
  

class CodeJudgeClient:
  
  SUPPORTED_LANGUAGES = ['python', 'cpp']

  def __init__(self, url="http://localhost:8000", test_case_dir="/sgl-workspace/data/test_cases/", do_sever_test=True):
    self.url = url
    if do_sever_test:
      self.sever_test()
    self.max_retry = 3
    self.darkbzoj_test_case_path_template = test_case_dir + "/darkbzoj/{problem_id}.zip"
  
  def sever_test(self):
    """
    Run a series of tests to ensure the server is working correctly.
    """
    test_all(self.url)

  def _judge_single(self, code, input_str, expected_output, lang='python'):
    assert lang in self.SUPPORTED_LANGUAGES, f"Unsupported language: {lang}. Supported languages are: {self.SUPPORTED_LANGUAGES}"
    data = {
            "type": lang,
            "solution": code,
            "input": input_str,
            "expected_output": expected_output
        }
    endpoint = 'judge'
    url = f"{self.url}/{endpoint}"
    response = requests.post(url, json=data)
    return response
  
  def parse_judge_response(self, response) -> JudgeResultType:
    # Delegate to dict-based parser
    try:
      if not response["run_success"]:
        reason = response["reason"]
        if reason == 'worker_timeout':
          return JudgeResultType.TLE
        elif reason == 'queue_timeout':
          return JudgeResultType.OJE
        else:
          return JudgeResultType.ER
      if not response["success"]:
        return JudgeResultType.WA
      return JudgeResultType.AC
    except Exception as e:
      print(f"Error parsing response: {e}")
      return JudgeResultType.OJE
  
  def parse_submission_result(self, result: SubmissionResult) -> JudgeResultType:
    if result.run_success is False:
      reason = result.reason
      if reason == 'worker_timeout':
        return JudgeResultType.TLE
      elif reason == 'queue_timeout':
        return JudgeResultType.OJE
      else:
        return JudgeResultType.ER
    if result.success is False:
      return JudgeResultType.WA
    return JudgeResultType.AC
        
  def judge_single(self, code, input_str, expected_output, lang='python'):
    for attempt in range(self.max_retry):
      try:
        response = self._judge_single(code, input_str, expected_output, lang)
        if response.status_code == 200:
          res = self.parse_judge_response(response.json())
          if res == JudgeResultType.OJE:
             pass
          else:
            return res
      except requests.RequestException as e:
        print(f"Request failed: {e}, retrying {attempt + 1}/{self.max_retry}")
    print("Max retries reached, returning OJE")
    return JudgeResultType.OJE

  def _judge_batch(self, submissions: List[Dict]) -> List[JudgeResultType]:
    """
    Send submissions as a long-batch request.
    Reuse parse_judge_response logic for each result dict.
    """
    required = {'code', 'input_str', 'expected_output', 'lang'}
    submissions_to_post = []
    for sub in submissions:
      assert required.issubset(sub.keys()), \
        f"Submission missing keys {required - sub.keys()}"
      lang = sub['lang']
      assert lang in self.SUPPORTED_LANGUAGES, \
        f"Unsupported language: {lang}. Supported: {self.SUPPORTED_LANGUAGES}"
      submissions_to_post.append({
        'type': lang,
        'solution': sub['code'],
        'input': sub['input_str'],
        'expected_output': sub['expected_output']
      })

    # Choose endpoint
    endpoint = 'judge/long-batch'
    url = f"{self.url}/{endpoint}"
    data = {'type': 'batch', 'submissions': submissions_to_post}
    response = requests.post(url, json=data)
    results_json = response.json()["results"]
    # Parse each result using existing parser
    judge_results: List[JudgeResultType] = []
    for res in results_json:
      judge_results.append(self.parse_judge_response(res))
    return judge_results

  def judge_batch(self, submissions: List[Dict]) -> List[JudgeResultType]:
    """
    Judge multiple submissions with retry only on OJE results.
    """
    # Initial batch
    results = self._judge_batch(submissions)
    # Retry only submissions that resulted in OJE
    for attempt in range(1, self.max_retry):
      # Find indices to retry
      to_retry = [i for i, r in enumerate(results) if r == JudgeResultType.OJE]
      if len(to_retry) == 0:
        break
      # Prepare submissions for retry
      retry_subs = [submissions[i] for i in to_retry]
      print(f"Retrying {len(retry_subs)} OJE submissions, attempt {attempt+1}/{self.max_retry}")
      retry_results = self._judge_batch(retry_subs)
      # Update only OJE slots
      for idx, new_res in zip(to_retry, retry_results):
        results[idx] = new_res
    return results

  def judge_darkbzoj(self, code: str, problem_id: str, lang: str="python") -> List[JudgeResultType]:
    """
    Judge a problem on DarkBZOJ using the provided code.
    Downloads test cases from the specified path.
    """
    assert lang in self.SUPPORTED_LANGUAGES, f"Unsupported language: {lang}. Supported languages are: {self.SUPPORTED_LANGUAGES}"
    test_case_path = self.darkbzoj_test_case_path_template.format(problem_id=problem_id)
    all_io_pairs = load_test_case_io_pairs_from_zip(test_case_path)
    
    submissions = []
    for input_str, expected_output in all_io_pairs:
      submissions.append({
        'code': code,
        'input_str': input_str,
        'expected_output': expected_output,
        'lang': lang
      })
    
    return self.judge_batch(submissions)
  
  def judge_darkbzoj_long_batch(self, all_darkbzoj_submissions: List[DarkbzojSubmission]) -> List[List[JudgeResultType]]:
    """
    Judge multiple DarkBZOJ submissions in a long-batch manner.
    Each submission is a DarkbzojSubmission object.
    Returns a list of results for each submission.
    """
    n_test_case_foreach_problem: List[int] = []
    tot_test_cases = 0
    all_async_submissions: List[Submission] = []
    for darkbzoj_submission in all_darkbzoj_submissions:
      current_index = len(n_test_case_foreach_problem) + 1     
      if current_index % 50 == 0:
        print(f"Loading test cases: {current_index}/{len(all_darkbzoj_submissions)}")
      assert isinstance(darkbzoj_submission, DarkbzojSubmission), \
        f"Expected DarkbzojSubmission, got {type(darkbzoj_submission)}"
      assert darkbzoj_submission.lang in self.SUPPORTED_LANGUAGES, \
        f"Unsupported language: {darkbzoj_submission.lang}. Supported languages are: {self.SUPPORTED_LANGUAGES}"
      test_case_path = self.darkbzoj_test_case_path_template.format(problem_id=darkbzoj_submission.problem_id)
      try:
        all_io_pairs = load_test_case_io_pairs_from_zip(test_case_path)
      except FileNotFoundError:
        print(f"Test case file not found: {test_case_path}. Skipping submission.")
        all_io_pairs = []
      except Exception as e:
        # raise RuntimeError(f"Failed to load test cases from {test_case_path}: {e}")
        print(f"Error loading test cases from {test_case_path}: {e}. Skipping submission.")
        all_io_pairs = []
      n_test_case_foreach_problem.append(len(all_io_pairs))
      tot_test_cases += len(all_io_pairs)

      for input_str, expected_output in all_io_pairs:
        # set a uuid for each submission
        sub_id = f"darkbzoj_{darkbzoj_submission.problem_id}_" + str(uuid.uuid4())
        all_async_submissions.append(Submission(
          sub_id=sub_id,
          type=darkbzoj_submission.lang,
          solution=darkbzoj_submission.code,
          input=input_str,
          expected_output=expected_output
        ))

    with QueuedJudgeClient(self.url, max_batch_size=480, max_workers=64) as qjc:
      qjc.submit(all_async_submissions)
      all_results = qjc.get_results()


    # Parse results into JudgeResultType
    all_judge_results: List[List[JudgeResultType]] = []
    assert len(all_results) == tot_test_cases, \
      f"Expected {tot_test_cases} results, got {len(all_results)}"

    idx = 0
    for n_cases in n_test_case_foreach_problem:
      problem_results = []
      for _ in range(n_cases):
        res: SubmissionResult = all_results[idx][1]
        assert res.sub_id == all_async_submissions[idx].sub_id, \
          f"Submission ID mismatch: {res.sub_id} != {all_async_submissions[idx].sub_id}"
        res = self.parse_submission_result(res)
        problem_results.append(res)
        idx += 1
      if len(problem_results) == 0:
        problem_results = [JudgeResultType.OJE]  # No test cases, assume OJE
      all_judge_results.append(problem_results)
    return all_judge_results

  def judge_results_to_text_summary(self, results: List[JudgeResultType]) -> str:
    """
    Convert a list of JudgeResultType to a human-readable summary.
    """
    result_type_count = collections.Counter(results)
    summary = ""
    for result_type in result_type_count:
      # write a percentage summary
      percentage = (result_type_count[result_type] / len(results)) * 100
      summary += f"  {JudgeResultTypeToHumanReadable[result_type]}: {percentage:.2f}%  |"
    return summary.strip()

if __name__ == '__main__':
  client = CodeJudgeClient("http://localhost:8009", do_sever_test=False)
  code = open("examples/code_judge/solution2378.cpp", "r").read()
  # results = client.judge_darkbzoj(code, "2378", lang="cpp")
  # print("Results:", results)
  # print("Summary:", client.judge_results_to_text_summary(results))
  all_darkbzoj_submissions = [
    DarkbzojSubmission(code=code, problem_id="2378", lang="cpp"),
    DarkbzojSubmission(code=code, problem_id="2378", lang="cpp"),
    DarkbzojSubmission(code=code, problem_id="2378", lang="python"),
    DarkbzojSubmission(code=code, problem_id="2378", lang="cpp"),
  ]
  # import asyncio
  # results = asyncio.run(client.judge_darkbzoj_long_batch(all_darkbzoj_submissions))
  results = client.judge_darkbzoj_long_batch(all_darkbzoj_submissions)
  for i, res in enumerate(results):
    print(f"Problem {i} results: {res}")
    print("Summary:", client.judge_results_to_text_summary(res))

