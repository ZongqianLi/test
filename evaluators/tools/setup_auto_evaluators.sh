mkdir -p /tmp/auto_evaluators
cp /mnt/mnhotzc/src/auto_evaluators/evaluators-250619.zip /tmp/auto_evaluators/

cd /tmp/auto_evaluators
unzip -o evaluators-250619.zip

EVALUATORS_HOME=/tmp/auto_evaluators/evaluators
cd $EVALUATORS_HOME

pip install aiohttp==3.12.13

pip install -e ./src
bash tools/start_code_judge.sh