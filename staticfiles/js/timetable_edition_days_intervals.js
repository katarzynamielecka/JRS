document.querySelectorAll(".lesson").forEach((lesson) => {
    lesson.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("lesson_id", lesson.dataset.lessonId);
    });
});

document.querySelectorAll(".droppable").forEach((cell) => {
    cell.addEventListener("dragover", (e) => {
        e.preventDefault();
    });

    cell.addEventListener("drop", (e) => {
        e.preventDefault();

        const lessonId = e.dataTransfer.getData("lesson_id");
        const day = cell.dataset.day;
        const intervalId = cell.closest("tr").dataset.intervalId;

        const payload = {
            lesson_id: lessonId,
            day: day,
            interval_id: intervalId,
        };

        const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

        fetch("/systemadmin/timetable/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,  
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Plan zaktualizowany!");
                    location.reload();
                } else {
                    alert(data.error || "Wystąpił błąd.");
                }
            })
            .catch((error) => {
                console.error("Błąd:", error);
            });
    });
});
