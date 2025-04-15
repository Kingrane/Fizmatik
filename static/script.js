document.getElementById('solver-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch('/solve', {
            method: 'POST',
            body: formData  // Отправляем FormData, а не JSON
        });

        if (!response.ok) {
            throw new Error('Ошибка сервера');
        }

        const data = await response.json();

        if (data.error) {
            document.getElementById('result').innerHTML =
                `<div class="error">${data.error}</div>`;
        } else {
            // Перенаправляем на страницу с решением
            window.location.href = `/solve-page?problem=${encodeURIComponent(data.problem)}&solution=${encodeURIComponent(data.solution)}`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML =
            `<div class="error">Ошибка соединения: ${error.message}</div>`;
        console.error('Ошибка:', error);
    }
});