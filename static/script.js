let badProxies = [];

function checkProxies(proxiesToCheck = null) {
    const textarea = document.getElementById('proxyInput');
    const allProxies = textarea.value.trim().split('\n').filter(line => line);
    const proxies = proxiesToCheck || allProxies;

    if (proxies.length === 0) {
        alert("Vui lòng nhập ít nhất 1 proxy.");
        return;
    }

    badProxies = [];  // Reset lại trước khi kiểm tra mới
    const list = document.getElementById('proxyStatusList');
    list.innerHTML = '';

    proxies.forEach(proxy => {
        const li = document.createElement('li');
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.innerHTML = `<span>${proxy}</span><span class="text-muted">Đang kiểm tra...</span>`;
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
                li.classList.add("list-group-item-success");
                li.innerHTML = `<span>${result.proxy}</span>
                                <span>${result.flag} ${result.country} – ${result.protocol}</span>`;
            } else {
                li.classList.add("list-group-item-danger");
                li.innerHTML = `<span>${result.proxy}</span><span>❌ Không hoạt động</span>`;
                badProxies.push(result.proxy);  // ← Cập nhật proxy lỗi
            }
        });
    })
    .catch(error => {
        alert("Lỗi kiểm tra proxy!");
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
