const { ipcRenderer } = require('electron');

document.getElementById('devtools-button').addEventListener('click', () => {
  ipcRenderer.send('open-devtools');
});

document.getElementById('console-button').addEventListener('click', () => {
  ipcRenderer.send('console-log', 'Debug message from the button!');
  console.log('Debug message from the button!');
});

document.getElementById('close-button').addEventListener('click', () => {
  ipcRenderer.send('close-app');
});
