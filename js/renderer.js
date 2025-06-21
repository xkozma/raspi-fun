const { ipcRenderer } = require('electron');
//const { getWeather } = require('./api.js');

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

// Fetch and display weather data
async function updateWeather() {
  const weather = await getWeather();
  if (weather) {
    document.getElementById('weather').textContent = `Weather: ${weather.temperature}°C`;
  } else {
    document.getElementById('weather').textContent = 'Weather: Unable to fetch data';
  }
}

// Call updateWeather on load
updateWeather();

// Fetch weather data every 5 minutes
setInterval(updateWeather, 5 * 60 * 1000);

// Placeholder for weather and reminders
document.getElementById('reminders').textContent = 'Reminders: No upcoming events';
document.getElementById('smart-home').textContent = 'Smart Home: Placeholder';
