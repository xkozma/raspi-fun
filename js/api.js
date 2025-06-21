// Function to fetch weather data using Open-Meteo
async function getWeather() {
    console.log('Fetching weather data...');
    const latitude = 48.1486; // Latitude for Bratislava, Slovakia
    const longitude = 17.1077; // Longitude for Bratislava, Slovakia
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true`;

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Failed to fetch weather data');
    }

    const data = await response.json();
    console.log(data)
    const temperature = data.current_weather.temperature;
    console.log(`The current temperature is ${temperature}°C`);
    return {
        temperature: temperature
    };
}

getWeather().catch(console.error);