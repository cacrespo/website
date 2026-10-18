document.addEventListener("DOMContentLoaded", function () {
    const linkInput = document.getElementById("id_link");
    if (!linkInput) {
        return;
    }

    // Create autofill button
    const button = document.createElement("button");
    button.type = "button";
    button.id = "ai-autofill-btn";
    button.className = "button";
    button.textContent = "✨ Completar con IA";
    button.style.marginLeft = "10px";
    button.style.backgroundColor = "#28a745";
    button.style.color = "#ffffff";
    button.style.fontWeight = "bold";
    button.style.cursor = "pointer";
    button.style.verticalAlign = "middle";

    // Status message span
    const statusSpan = document.createElement("span");
    statusSpan.id = "ai-autofill-status";
    statusSpan.style.marginLeft = "10px";
    statusSpan.style.fontSize = "0.9em";
    statusSpan.style.verticalAlign = "middle";

    // Insert button and status right next to link input
    linkInput.parentNode.insertBefore(statusSpan, linkInput.nextSibling);
    linkInput.parentNode.insertBefore(button, statusSpan);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    button.addEventListener("click", async function () {
        const urlValue = linkInput.value.trim();
        if (!urlValue) {
            statusSpan.style.color = "#dc3545";
            statusSpan.textContent = "⚠️ Por favor, ingresa una URL primero.";
            return;
        }

        button.disabled = true;
        button.textContent = "⏳ Extrayendo datos con IA...";
        statusSpan.style.color = "#6c757d";
        statusSpan.textContent = "Analizando el artículo...";

        const csrfToken =
            document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
            getCookie("csrftoken");

        try {
            const response = await fetch("/api/v1/articles/extract/", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ url: urlValue }),
            });

            const contentType = response.headers.get("content-type") || "";
            let data = null;

            if (contentType.includes("application/json")) {
                data = await response.json();
            } else {
                if (response.status === 403) {
                    statusSpan.style.color = "#dc3545";
                    statusSpan.textContent =
                        "❌ Error 403: Sesión o verificación CSRF falló. Recarga la página e intenta nuevamente.";
                    return;
                }
                statusSpan.style.color = "#dc3545";
                statusSpan.textContent = `❌ Error del servidor (${response.status} ${response.statusText}).`;
                return;
            }

            if (!response.ok) {
                const errorMsg =
                    data.error ||
                    (data.url ? data.url.join(" ") : "Error al extraer datos.");
                statusSpan.style.color = "#dc3545";
                statusSpan.textContent = `❌ ${errorMsg}`;
                return;
            }

            const titleInput = document.getElementById("id_title");
            const authorInput = document.getElementById("id_author");
            const commentInput = document.getElementById("id_comment");

            if (titleInput && data.title) {
                titleInput.value = data.title;
            }
            if (authorInput && data.author) {
                authorInput.value = data.author;
            }
            if (commentInput && data.description) {
                commentInput.value = data.description;
            }

            statusSpan.style.color = "#28a745";
            statusSpan.textContent = "✅ ¡Campos completados! Revisa y guarda cuando quieras.";
        } catch (err) {
            statusSpan.style.color = "#dc3545";
            statusSpan.textContent = `❌ Error: ${err.message}`;
        } finally {
            button.disabled = false;
            button.textContent = "✨ Completar con IA";
        }
    });
});
