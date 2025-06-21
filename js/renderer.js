const { ipcRenderer } = require('electron');

// Toggle settings menu visibility
document.getElementById('settings-button').addEventListener('click', (event) => {
  event.stopPropagation(); // Prevent click from propagating to the document
  const settingsMenu = document.getElementById('settings-menu');
  settingsMenu.style.display = settingsMenu.style.display === 'none' ? 'block' : 'none';
});

// Close settings menu when clicking outside
document.addEventListener('click', (event) => {
  const settingsMenu = document.getElementById('settings-menu');
  if (settingsMenu.style.display === 'block' && !settingsMenu.contains(event.target)) {
    settingsMenu.style.display = 'none';
  }
});

// DevTools button functionality
document.getElementById('devtools-button').addEventListener('click', () => {
  ipcRenderer.send('open-devtools');
});

// Console button functionality
document.getElementById('console-button').addEventListener('click', () => {
  ipcRenderer.send('console-log', 'Debug message from the button!');
  console.log('Debug message from the button!');
});

document.getElementById('close-button').addEventListener('click', () => {
  ipcRenderer.send('close-app');
});

// Function to update the time and date
function updateTimeAndDate() {
  const now = new Date();
  document.getElementById('time').textContent = now.toLocaleTimeString();
  document.getElementById('date').textContent = now.toLocaleDateString();
}

// Update time and date every second
setInterval(updateTimeAndDate, 1000);
updateTimeAndDate(); // Initial call to set values immediately

// Placeholder for weather and reminders
document.getElementById('weather').textContent = 'Weather: Sunny, 25°C';
document.getElementById('reminders').textContent = 'Reminders: No upcoming events';
document.getElementById('smart-home').textContent = 'Smart Home: Placeholder';
