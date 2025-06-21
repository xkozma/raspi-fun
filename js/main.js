const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
//const renderer = require('./renderer.js'); // Assuming you have a renderer.js file

function createWindow() {
  const win = new BrowserWindow({
    width: 640,
    height: 480,
    frame: false, // Make the window borderless
    webPreferences: {
      preload: path.join(__dirname,'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.setMenuBarVisibility(false); // Hide the menu bar

  win.loadFile('index.html');
  win.webContents.openDevTools({ mode: 'detach', activate: true });
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

  ipcMain.on('toggle-dark-mode', (event, isDarkMode) => {
    console.log(`Dark mode is now ${isDarkMode ? 'enabled' : 'disabled'}`);
  });

  ipcMain.on('toggle-settings-menu', (event, isVisible) => {
    console.log(`Settings menu is now ${isVisible ? 'visible' : 'hidden'}`);
  });
}

app.whenReady().then(() => {
  createWindow();

  // Boot up in dark mode
  setTimeout(() => {
    BrowserWindow.getAllWindows()[0].webContents.send('toggle-dark-mode', true);
  }, 100);

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
    app.quit();

});

ipcMain.on('close-app', () => {
  app.quit();
});
