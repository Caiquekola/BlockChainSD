@echo off
echo Starting Blockchain Nodes...

echo Starting Node A on port 5000...
start "Node A" cmd /k "python run_node.py 5000 NodeA"

timeout /t 2 /nobreak >nul

echo Starting Node B on port 5001...
start "Node B" cmd /k "python run_node.py 5001 NodeB"

timeout /t 2 /nobreak >nul

echo Starting Node C on port 5002...
start "Node C" cmd /k "python run_node.py 5002 NodeC"

echo All nodes started!
echo.
echo Access the nodes at:
echo Node A: http://localhost:5000
echo Node B: http://localhost:5001
echo Node C: http://localhost:5002
echo.
pause
