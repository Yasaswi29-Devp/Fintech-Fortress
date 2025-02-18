// Add ZKP visual feedback
document.querySelector('.login-form').addEventListener('submit', function(e) {
    const accountNumber = document.getElementById('account_number').value;
    if (accountNumber === '0') {
        // Show ZKP process for admin login
        const statusDiv = document.createElement('div');
        statusDiv.className = 'zkp-status';
        statusDiv.innerHTML = `
            <h4>ZKP Authentication Process</h4>
            <div class="zkp-step">Generating proof...</div>
            <div class="zkp-step">Verifying...</div>
        `;
        this.appendChild(statusDiv);
    }
});
