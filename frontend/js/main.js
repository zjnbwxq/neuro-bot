const API_BASE_URL = 'https://api.neuro-farm.com';

async function getUserInfo(discordId) {
    const response = await fetch(`${API_BASE_URL}/api/users/${discordId}`);
    const user = await response.json();
    document.getElementById('user-info').innerHTML = `
        <h2>User Info</h2>
        <p>Discord ID: ${user.discord_id}</p>
        <p>Language: ${user.language}</p>
        <p>Coins: ${user.coins}</p>
        <p>Experience: ${user.experience}</p>
    `;
}

async function getFarmInfo(userId) {
    const response = await fetch(`${API_BASE_URL}/api/farms/${userId}`);
    const farm = await response.json();
    document.getElementById('farm-info').innerHTML = `
        <h2>Farm Info</h2>
        <p>Farm Name: ${farm.name}</p>
        <p>Farm Level: ${farm.level}</p>
    `;
}

// 调用这些函数，传入实际的 Discord ID 和用户 ID
getUserInfo('some_discord_id');
getFarmInfo(1);
