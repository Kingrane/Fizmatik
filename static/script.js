document.getElementById('solver-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const form = e.target;
    const problem = form.problem.value.trim();
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = "Решаю... ⏳";

    try {
        const response = await fetch('/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ problem })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Неизвестная ошибка.");
        }

        resultDiv.innerHTML = `
            <h3>Задача:</h3>
            <p>${data.problem}</p>
            <h3>Решение:</h3>
            <p>${data.solution}</p>
            <a href="/solve-page?problem=${encodeURIComponent(data.problem)}&solution=${encodeURIComponent(data.solution)}">Открыть на отдельной странице</a>
        `;

        if (window.MathJax) MathJax.typeset(); // Рендер LaTeX
    } catch (err) {
        resultDiv.innerHTML = `<p style="color: red;">Ошибка: ${err.message}</p>`;
    }
});
