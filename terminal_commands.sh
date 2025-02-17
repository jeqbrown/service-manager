# Find the process using port 8000
sudo lsof -i :8000

# Kill the process (replace PID with the actual process ID)
kill PID
# Or force kill if necessary
kill -9 PID