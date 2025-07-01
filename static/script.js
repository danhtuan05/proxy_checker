let badProxies = [];

function checkProxies(proxiesToCheck = null) {
    const textarea = document.getElementById('proxyInput');
    const allProxies = textarea.value.trim().split('\n').filter(line => line);
    const proxies = proxiesToCheck || allProxies;

    if (proxies.length === 0) {
        alert("Vui lòng nhập ít nhất 1 proxy.");
        return;
    }

    badProxies = [];  // reset lại danh sách lỗi

    const list = document.getElementById('proxyStatusList');
    list.innerHTML = '';

    proxies.forEach(proxy => {
        const li = document.createElement('li');
        li.className = "list-group-item";
        li.innerHTML = `
            <div class="w-100">
                <div class="fw-bold text-break">${proxy}</div>
                <div class="text-muted small">Đang kiểm tra...</div>
            </div>
        `;
        list.appendChild(li);
    });

    fetch('/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proxies })
    })
    .then(response => response.json())
    .then(results => {
        results.forEach((result, i) => {
            const li = list.children[i];
            if (result.working) {
                li.classList.remove("list-group-item-danger");
                li.classList.add("list-group-item-success");
                li.innerHTML = `
                    <div class="w-100">
                        <div class="fw-bold text-break">${result.proxy}</div>
                        <div class="text-muted small">${result.flag} ${result.country} – ${result.protocol}</div>
                    </div>
                `;
            } else {
                li.classList.remove("list-group-item-success");
                li.classList.add("list-group-item-danger");
                li.innerHTML = `
                    <div class="w-100">
                        <div class="fw-bold text-break">${result.proxy}</div>
                        <div class="text-danger small">❌ Không hoạt động</div>
                    </div>
                `;
                badProxies.push(result.proxy);
            }
        });
    })
    .catch(error => {
        alert("Lỗi khi kiểm tra proxy.");
        console.error(error);
    });
}


function recheckBadProxies() {
    if (badProxies.length === 0) {
        alert("Không có proxy lỗi để kiểm tra lại.");
        return;
    }
    checkProxies(badProxies);  // Gọi lại hàm chính với danh sách lỗi
}
function clearProxyInput() {
    document.getElementById('proxyInput').value = '';
}
