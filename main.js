const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 480,
    height: 320,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadFile('index.html');

  ipcMain.on('open-devtools', () => {
    try {
      win.webContents.openDevTools({ mode: 'detach', activate: true });
      console.log('DevTools opened successfully');
      if (win.webContents.devToolsWebContents) {
        win.webContents.devToolsWebContents.focus();
      }
    } catch (err) {
      console.error('Failed to open DevTools:', err);
    }
  });

  ipcMain.on('console-log', (event, message) => {
    console.log('Renderer log:', message);
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
