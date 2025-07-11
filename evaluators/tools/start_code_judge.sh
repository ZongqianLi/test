if [ "$(whoami)" = "root" ]; then
  apt-get update
  apt-get install redis -y
  apt-get install bubblewrap
else
  sudo apt-get update
  sudo apt-get install redis -y
  sudo apt-get install bubblewrap
fi

redis-server --daemonize yes

cd /tmp/auto_evaluators/evaluators/third_party/code-judge-main-250619

pip install -r requirements.txt --user
pip install -r requirements.txt

# sudo apt-get install firejail -y
# export PYTHON_EXECUTE_COMMAND='firejail --read-only=/ --net=none --whitelist={workdir} --quiet -- python3 {source}'
# export CPP_COMPILE_COMMAND='firejail --read-only=/ --net=none --whitelist={workdir} --quiet -- g++ -O2 -o {exe} {source}'
# export CPP_EXECUTE_COMMAND='firejail --read-only=/ --net=none --whitelist={workdir} --quiet -- {exe}'


export PYTHON_EXECUTE_COMMAND='bwrap --ro-bind / / --unshare-all --dev-bind /dev /dev --die-with-parent --bind {workdir} {workdir} -- python3 {source}'
export CPP_COMPILE_COMMAND='bwrap --ro-bind / / --unshare-all --dev-bind /dev /dev --die-with-parent --bind {workdir} {workdir} -- g++ -O2 -o {exe} {source}'
export CPP_EXECUTE_COMMAND='bwrap --ro-bind / / --unshare-all --dev-bind /dev /dev --die-with-parent --bind {workdir} {workdir} -- {exe}'



# REDIS_URI=redis://localhost:6379 python debug_api.py > /tmp/code_judge.log 2>&1 &

REDIS_URI=redis://localhost:6379 uvicorn app.main:app --workers 96 --limit-max-requests 2048 --host 0.0.0.0 --port 8009 > /tmp/uvicorn_code_judge.log 2>&1 &
REDIS_URI=redis://localhost:6379 python run_code_judge_workers.py > /tmp/code_judge_workers.log 2>&1 &