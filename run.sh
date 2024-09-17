#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

# Start the backend server
echo "Starting the backend server..."
nohup python server.py > server.log 2>&1 &
BACKEND_PID=$!
echo "Backend server started with PID $BACKEND_PID"

# Wait for the backend server to start (adjust the sleep time if needed)
sleep 5

# Start the Streamlit frontend on port 5000
echo "Starting the Streamlit frontend..."
nohup streamlit run app.py --server.port 8080 > frontend.log 2>&1 &  
FRONTEND_PID=$!
echo "Streamlit frontend started with PID $FRONTEND_PID"

# Save the PIDs to a file for easy shutdown later
echo $BACKEND_PID > pids.txt
echo $FRONTEND_PID >> pids.txt

echo "Both processes are now running in the background."
echo "You can view the backend logs in backend.log"
echo "You can view the frontend logs in frontend.log"
echo "To stop the processes, run: ./stop.sh"

# Display the Streamlit access link
echo "Access the Streamlit frontend at: http://localhost:8080"

# Create a stop script
cat << EOF > stop.sh
#!/bin/bash
if [ -f pids.txt ]; then
    while read pid; do
        if ps -p \$pid > /dev/null; then
            echo "Stopping process \$pid"
            kill \$pid
        fi
    done < pids.txt
    rm pids.txt
    echo "All processes stopped"
else
    echo "No pids.txt file found. Processes may not be running."
fi
EOF

chmod +x stop.sh

echo "A stop script has been created. Run ./stop.sh to stop the processes."