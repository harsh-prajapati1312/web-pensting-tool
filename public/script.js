const socket = io();
    const inputBox = document.getElementById('input-box');
    const runButton = document.getElementById('run-button');
    const terminalOutput = document.getElementById('terminal-output');
    const clearButton = document.getElementById('clear-button');
    const exportButton = document.getElementById('export-button');
    const terminalControls = document.getElementById('terminal-controls');
    
    runButton.addEventListener('click', () => {
      const input = inputBox.value;
      socket.emit('run-script', input);
      terminalOutput.innerHTML = '';
      terminalControls.classList.remove('hidden', 'opacity-0');
      terminalControls.classList.add('opacity-100');
      terminalOutput.classList.remove('hidden', 'opacity-0', 'scale-95');
      terminalOutput.classList.add('opacity-100', 'scale-100');
    });
    
    socket.on('output', (output) => {
      terminalOutput.innerHTML += output.replace(/\n/g, '<br>');
      terminalOutput.scrollTop = terminalOutput.scrollHeight;
    });
    
    socket.on('file-contents', (fileContents) => {
      console.log('Received file contents:', fileContents);
      const downloadLinks = document.createElement('div');
      downloadLinks.innerHTML = '<h3 class="text-lg font-semibold mb-2">Download Files:</h3>';
    
      for (const fileName in fileContents) {
        const fileContent = fileContents[fileName];
        const blob = new Blob([fileContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
    
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        link.textContent = fileName;
        link.classList.add('block', 'text-blue-500', 'hover:text-blue-700', 'mb-1');
        downloadLinks.appendChild(link);
      }
    
      terminalOutput.appendChild(downloadLinks);
    });
    
    clearButton.addEventListener('click', () => {
      terminalOutput.innerHTML = '';
    });
    
    exportButton.addEventListener('click', () => {
      const text = terminalOutput.innerText;
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'terminal-output.txt';
      a.click();
      URL.revokeObjectURL(url);
    });
