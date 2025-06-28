let badProxies = [];

function showLoading(show) {
    document.getElementById("loading").style.display = show ? "block" : "none";
}

function checkProxies() {
    const textarea = document.getElementById('proxyInput');
    const proxies = textarea.value.trim().split('\n').filter(line => line);

    if (proxies.length === 0) {
        alert("Vui lòng nhập ít nhất 1 proxy.");
        return;
    }

    showLoading(true);
    fetch('/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proxies: proxies })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        updateResults(data.working, data.not_working);
    });
}

function recheckBadProxies() {
    if (badProxies.length === 0) {
        alert("Không có proxy lỗi nào để kiểm tra lại.");
        return;
    }

    showLoading(true);
    fetch('/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proxies: badProxies })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        updateResults(data.working, data.not_working);
    });
}

function updateResults(working, notWorking) {
    const workingList = document.getElementById('workingList');
    const notWorkingList = document.getElementById('notWorkingList');

    workingList.innerHTML = '';
    notWorkingList.innerHTML = '';

    working.forEach(p => {
        const li = document.createElement('li');
        li.className = "list-group-item list-group-item-success";
        li.textContent = p;
        workingList.appendChild(li);
    });

    notWorking.forEach(p => {
        const li = document.createElement('li');
        li.className = "list-group-item list-group-item-danger";
        li.textContent = p;
        notWorkingList.appendChild(li);
    });

    badProxies = notWorking;
}
