if (!auth.isAuthenticated()) {
    window.location.href = '/login.html';
}
let clients;
// Загрузка сделок
async function loadClients() {
    try {
         clients = await api.get('/api/clients/');
    } catch (error) {
        console.error('Ошибка загрузки клиентов:', error);
    }
}
(async function () {
    await loadClients();
})();