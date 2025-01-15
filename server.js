const express = require('express');
    const http = require('http');
    const { Server } = require('socket.io');
    const { spawn } = require('child_process');
    const path = require('path');
    
    const app = express();
    const server = http.createServer(app);
    const io = new Server(server);
    
    app.use(express.static(path.join(__dirname, 'public')));
    
    io.on('connection', (socket) => {
      console.log('Client connected');
    
      socket.on('run-script', (input) => {
        try {
          const pythonProcess = spawn('python3', ['bug_bounty.py', input], {
            cwd: __dirname,
          });
    
          pythonProcess.stdout.on('data', (data) => {
            socket.emit('output', data.toString());
          });
    
          pythonProcess.stderr.on('data', (data) => {
             socket.emit('output', data.toString());
          });
    
          pythonProcess.on('close', (code) => {
             pythonProcess.stdout.on('data', (data) => {
              if (data.includes('File contents:')) {
                try {
                  const fileContents = JSON.parse(data.toString().split('File contents: ')[1].replace(/'/g, '"'));
                  socket.emit('file-contents', fileContents);
                } catch (e) {
                  console.error("Error parsing file contents:", e);
                  socket.emit('output', `Error parsing file contents: ${e.message}`);
                }
              }
            });
            socket.emit('output', `\nProcess exited with code ${code}`);
          });
    
          pythonProcess.on('error', (err) => {
            socket.emit('output', `\nError: ${err.message}`);
          });
        } catch (error) {
          socket.emit('output', `\nError spawning process: ${error.message}`);
        }
      });
    
      socket.on('disconnect', () => {
        console.log('Client disconnected');
      });
    });
    
    const PORT = 3000;
    server.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
