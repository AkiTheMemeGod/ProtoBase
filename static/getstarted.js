// Sign-in form submission
document.getElementById("signinForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const username = document.getElementById("signinUsername").value;
    const password = document.getElementById("signinPassword").value;
    const output = document.getElementById("signinOutput");
    output.innerHTML = "<p>Processing...</p>";

    try {
        const response = await fetch('/signin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        if (result.success) {
            // Redirect to the dashboard
            window.location.href = "/dashboard";
        } else {
            output.innerHTML = `<p style="color: red;">${result.message || "Signin failed!"}</p>`;
        }
    } catch (error) {
        output.innerHTML = `<p style="color: red;">Server error. Please try again later.</p>`;
    }
});


// Sign-up form submission
document.getElementById("signupForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const username = document.getElementById("signupUsername").value;
    const password = document.getElementById("signupPassword").value;
    const output = document.getElementById("signupOutput");
    output.innerHTML = "<p>Processing...</p>";

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        if (result.success) {

            window.location.href = "/dashboard";
        } else {
            output.innerHTML = `<p style="color: red;">${result.message || "Signup failed!"}</p>`;
        }
    } catch (error) {
        output.innerHTML = `<p style="color: red;">Server error. Please try again later.</p>`;
    }
});


function showSignUp() {
    document.getElementById('sign-in-form').classList.add('hidden');
    document.getElementById('sign-up-form').classList.remove('hidden');
}

function showSignIn() {
    document.getElementById('sign-up-form').classList.add('hidden');
    document.getElementById('sign-in-form').classList.remove('hidden');
}

function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard');
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}
