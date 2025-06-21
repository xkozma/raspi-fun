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

const settingsButton = document.getElementById('settings-button');
const settingsMenu = document.getElementById('settings-menu');
const darkModeToggle = document.getElementById('dark-mode-toggle');
const settingsIcon = settingsButton.querySelector('img');
const turnOffButton = document.getElementById('turn-off-button');

let isDarkMode = true;
let mouseInTopArea = false;
let mouseInSettingsMenu = false;
let cursorTimeout;

// ipcRenderer.on('toggle-dark-mode', (event, enabled) => {
//   isDarkMode = enabled;
//   document.body.classList.toggle('dark-mode', isDarkMode);
//   settingsIcon.src = isDarkMode ? './assets/settings-icon-dark.png' : './assets/settings-icon.png';
// });

document.addEventListener('mousemove', (event) => {
  if (event.clientY <= 50 || mouseInSettingsMenu) { // Check if cursor is in top area or settings menu
    mouseInTopArea = true;
    toggleButtonsVisibility(true);
  } else {
    mouseInTopArea = false;
    setTimeout(() => {
      if (!mouseInTopArea && !mouseInSettingsMenu) {
        toggleButtonsVisibility(false);
      }
    }, 300); // Delay to allow for smooth transitions
  }
});

document.addEventListener('mousemove', () => {
  document.body.classList.remove('hide-cursor'); // Show cursor on movement
  clearTimeout(cursorTimeout); // Reset timeout
  cursorTimeout = setTimeout(() => {
    document.body.classList.add('hide-cursor'); // Hide cursor after inactivity
  }, 2000); // 2 seconds of inactivity
});

settingsMenu.addEventListener('mouseenter', () => {
  mouseInSettingsMenu = true;
  toggleButtonsVisibility(true);
});

settingsMenu.addEventListener('mouseleave', () => {
  mouseInSettingsMenu = false;
  setTimeout(() => {
    if (!mouseInTopArea && !mouseInSettingsMenu) {
      toggleButtonsVisibility(false);
    }
  }, 300);
});

settingsButton.addEventListener('click', () => {
  settingsMenu.classList.toggle('hidden');
});

darkModeToggle.addEventListener('click', () => {
  isDarkMode = !isDarkMode;
  document.body.classList.toggle('dark-mode', isDarkMode);
  ipcRenderer.send('toggle-dark-mode', isDarkMode);

  // Update settings icon based on dark mode
  settingsIcon.src = isDarkMode ? './assets/settings-icon-dark.png' : './assets/settings-icon.png';
});

turnOffButton.addEventListener('click', () => {
  const confirmExit = confirm('Are you sure you want to exit the application?');
  if (confirmExit) {
    ipcRenderer.send('close-app');
  }
});

function toggleButtonsVisibility(visible) {
  const elements = [settingsButton];
  elements.forEach(el => el.classList.toggle('hidden', !visible));
}
