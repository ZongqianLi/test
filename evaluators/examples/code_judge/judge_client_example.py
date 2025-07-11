from auto_evaluators.code.code_judge_client import CodeJudgeClient

client = CodeJudgeClient("http://localhost:8009")
code = open("examples/code_judge/solution2378.cpp", "r").read()
results = client.judge_darkbzoj(code, "2378", lang="cpp")
print("Results:", results)
print("Summary:", client.judge_results_to_text_summary(results))