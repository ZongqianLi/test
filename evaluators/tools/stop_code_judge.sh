#!/bin/bash
# filepath: /home/zewenchi/repo/evaluators/tools/stop_debug_api.sh

echo "Stopping uvicorn processes..."

# Find all uvicorn processes and kill them
pids=$(ps -ef | grep "[u]vicorn" | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "No uvicorn processes found."
else
    echo "Found uvicorn processes with PIDs: $pids"
    
    # Kill the processes gracefully first
    for pid in $pids; do
        echo "Stopping process $pid..."
        kill "$pid"
    done
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Check if any processes are still running and force kill if necessary
    remaining_pids=$(ps -ef | grep "[u]vicorn" | awk '{print $2}')
    
    if [ ! -z "$remaining_pids" ]; then
        echo "Some processes didn't stop gracefully. Force killing..."
        for pid in $remaining_pids; do
            echo "Force killing process $pid..."
            kill -9 "$pid"
        done
    fi
    
    echo "All uvicorn processes have been stopped."
fi


echo "Stopping run_code_judge_workers.py processes..."

# Find all run_code_judge_workers.py processes and kill them
pids=$(ps -ef | grep "[r]un_code_judge_workers.py" | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "No run_code_judge_workers.py processes found."
else
    echo "Found run_code_judge_workers.py processes with PIDs: $pids"
    
    # Kill the processes gracefully first
    for pid in $pids; do
        echo "Stopping process $pid..."
        kill "$pid"
    done
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Check if any processes are still running and force kill if necessary
    remaining_pids=$(ps -ef | grep "[r]un_code_judge_workers.py" | awk '{print $2}')
    
    if [ ! -z "$remaining_pids" ]; then
        echo "Some processes didn't stop gracefully. Force killing..."
        for pid in $remaining_pids; do
            echo "Force killing process $pid..."
            kill -9 "$pid"
        done
    fi
    
    echo "All run_code_judge_workers.py processes have been stopped."
fi

# Also stop redis server if it was started by the start script
echo "Stopping redis server..."
redis-cli shutdown 2>/dev/null || echo "Redis server was not running or already stopped."

echo "Done."