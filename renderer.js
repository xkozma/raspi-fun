const { ipcRenderer } = require('electron');

document.getElementById('devtools-button').addEventListener('click', () => {
  ipcRenderer.send('open-devtools');
});

document.getElementById('console-button').addEventListener('click', () => {
  console.log('Debug message from the button!');
});
