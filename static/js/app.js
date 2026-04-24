let isAdmin = false;
const bootstrapModals = {
    login: new bootstrap.Modal(document.getElementById("loginModal")),
    record: new bootstrap.Modal(document.getElementById("recordModal")),
    edit: new bootstrap.Modal(document.getElementById("editModal"))
};
document.addEventListener("DOMContentLoaded", () => {
    checkAuthStatus();
});

async function checkAuthStatus() {
    const res = await fetch("/api/auth/status");
    const data = await res.json();
    isAdmin = data.logged_in;

    document.getElementById("btnLogin").classList.toggle("d-none", isAdmin);
    document.getElementById("btnLogout").classList.toggle("d-none", !isAdmin);
    document.getElementById("btnAdd").classList.toggle("d-none", !isAdmin);

    document
        .querySelectorAll(".admin-col")
        .forEach((el) => el.classList.toggle("d-none", !isAdmin));
    loadRecords();
}

document.getElementById("submitLogin").addEventListener("click", async () => {
    const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value,
        }),
    });

    if (res.ok) {
        bootstrapModals.login.hide();
        checkAuthStatus();
    } else {
        alert("登入失敗");
    }
});

document.getElementById("btnLogout").addEventListener("click", async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    checkAuthStatus();
});

// [NEW] 完整實作渲染邏輯，並確保支援管理員權限切換
async function loadRecords(query = "", forceAll = false) {
    let url = `/api/records?q=${encodeURIComponent(query)}`;
    if (forceAll) url += "&all=true";

    const res = await fetch(url);
    const records = await res.json();
    const tbody = document.getElementById("recordTableBody");
    tbody.innerHTML = "";

    records.forEach((r) => {
        const tr = document.createElement("tr");
        const nameArray = r.names.split(/[,，\s]+/);
        const namesContainer = document.createElement("div");
        namesContainer.className = "names-cell";

        nameArray.forEach((name) => {
            if (name.trim()) {
                const div = document.createElement("div");
                div.textContent = name.trim();
                namesContainer.appendChild(div);
            }
        });

        // 構建操作按鈕 (僅在管理員模式顯示)
        const safeData = JSON.stringify(r).replace(/'/g, "&apos;");
        const adminBtns = isAdmin ? `
        <td class="text-center admin-col">
            <button class="btn btn-warning btn-sm me-1" onclick='openEditModal(${safeData})'>
                <i class="bi bi-pencil-square"></i> 編輯
            </button>
            <button class="btn btn-danger btn-sm" onclick="deleteRecord(${r.id})">
                <i class="bi bi-trash"></i> 刪除
            </button>
        </td>` : '<td class="admin-col d-none"></td>';

        tr.innerHTML = `
            <td>${r.id}</td>
            <td id="names-${r.id}"></td>
            <td>$${r.amount}</td>
            <td>${r.altar_name}</td>
            ${adminBtns}
        `;

        tbody.appendChild(tr);
        document.getElementById(`names-${r.id}`).appendChild(namesContainer);
    });
}

// [MODIFIED] 修正新增紀錄後的刷新邏輯 (約第 125 行)
document.getElementById("saveRecord").addEventListener("click", async () => {
    const payload = {
        names: document.getElementById("names").value,
        amount: parseInt(document.getElementById("amount").value),
        altar_name: document.getElementById("altarName").value,
    };

    await fetch("/api/records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    bootstrapModals.record.hide();

    // [NEW] 新增後自動顯示全部，確保使用者看到剛才新增的資料
    loadRecords('', true);

    document.getElementById("names").value = "";
    document.getElementById("amount").value = "";
    document.getElementById("altarName").value = "";
});

// [MODIFIED] 修正刪除紀錄後的刷新邏輯 (約第 142 行)
window.deleteRecord = async (id) => {
    if (!confirm("確認刪除此紀錄？")) return;
    await fetch(`/api/records/${id}`, { method: "DELETE" });

    // [NEW] 刪除後依照目前的搜尋框內容重新整理
    const q = document.getElementById('searchInput').value;
    loadRecords(q, q === '');
};

// [INSERT] 修正按鈕事件
document.getElementById('btnSearch').addEventListener('click', () => {
    loadRecords(document.getElementById('searchInput').value, false);
});

document.getElementById('btnShowAll').addEventListener('click', () => {
    document.getElementById('searchInput').value = '';
    loadRecords('', true); // [MODIFIED] 傳入 true 觸發後端 show_all
});

// [INSERT] 補全缺失的編輯視窗邏輯
window.openEditModal = (data) => {
    document.getElementById('editId').value = data.id;
    document.getElementById('editNames').value = data.names;
    document.getElementById('editAmount').value = data.amount;
    document.getElementById('editAltarName').value = data.altar_name;
    bootstrapModals.edit.show();
};

document.getElementById('updateRecord').addEventListener('click', async () => {
    const id = document.getElementById('editId').value;
    const payload = {
        names: document.getElementById('editNames').value,
        amount: parseInt(document.getElementById('editAmount').value),
        altar_name: document.getElementById('editAltarName').value
    };
    const res = await fetch(`/api/records/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (res.ok) {
        bootstrapModals.edit.hide();
        loadRecords(document.getElementById('searchInput').value, !document.getElementById('searchInput').value);
    }
});

// [INSERT] 於檔案末端
document.getElementById('btnExport').addEventListener('click', async () => {
    // 強制獲取完整資料庫紀錄 [cite: 5]
    const res = await fetch('/api/records?all=true');
    const records = await res.json();

    if (records.length === 0) {
        alert('無資料可匯出');
        return;
    }

    // 定義 CSV 標頭
    const headers = ['編號', '信眾姓名', '金額', '壇名'];

    // 處理資料行：將姓名中的換行、逗號與空白替換，避免破壞 CSV 結構
    const rows = records.map(r => [
        r.id,
        r.names.replace(/[\n\r,，\s]+/g, ' '),
        r.amount,
        r.altar_name
    ]);

    // 組合 CSV 內容：
    // 使用 "\uFEFF" (UTF-8 BOM) 是關鍵，確保 Excel 在繁體中文環境下開啟不亂碼
    const csvContent = "\uFEFF" + [headers, ...rows].map(e => e.join(",")).join("\n");

    // 建立 Blob 與下載連結
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    const dateStr = new Date().toISOString().split('T')[0];

    link.setAttribute("href", url);
    link.setAttribute("download", `點燈清單匯出_${dateStr}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});