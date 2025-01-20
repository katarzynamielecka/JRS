document.querySelectorAll(".lesson").forEach((lesson) => {
    lesson.addEventListener("dblclick", (e) => {
        const lessonId = lesson.dataset.lessonId;
        document.getElementById("lessonIdInput").value = lessonId;

        const modal = document.getElementById("editLessonModal");
        modal.style.display = "flex";
    });
});

document.querySelector(".modal .close").addEventListener("click", () => {
    document.getElementById("editLessonModal").style.display = "none";
});

document.getElementById("saveLessonChanges").addEventListener("click", () => {
    const lessonId = document.getElementById("lessonIdInput").value;
    const classroomId = document.getElementById("classroomSelect").value;
    const teacherId = document.getElementById("teacherSelect").value;

    const payload = {
        lesson_id: lessonId,
        classroom_id: classroomId,
        teacher_id: teacherId,
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
            alert("Zmiany zapisane!");
            location.reload();
        } else {
            alert(data.error || "Wystąpił błąd.");
        }
    })
    .catch((error) => {
        console.error("Błąd:", error);
    });

    document.getElementById("editLessonModal").style.display = "none";
});